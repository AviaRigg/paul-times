"""Turn Paul's encrypted taps (Google Sheet rows from his "Paul Times taps" form) into the state the paper uses.

Usage:  TPT_PASSWORD=xxxx python kit/screen_state.py rows.json <issue id>
Also prints Paul's unanswered flags and feedback notes (see RUNBOOK, Corrections).
rows.json: the Sheet's values as a JSON list of rows (what the Google Sheets connector returns), any shape;
every cell that starts with "tpt1." is decrypted, anything else (headers, junk, other people's spam) is ignored.
Writes issues/<id>/screen-state.json (gitignored; the build puts it inside the encrypted issue so his phone
gets it back) and prints a summary to use when writing the Screen section.
"""
import base64, json, os, sys
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
rows_path, iid = sys.argv[1], sys.argv[2]
pw = os.environ.get("TPT_PASSWORD") or sys.exit("Set TPT_PASSWORD")
cfg = json.load(open(os.path.join(ROOT, "docs", "crypto.json")))
aes = AESGCM(PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=base64.b64decode(cfg["salt"]),
                        iterations=cfg["iterations"]).derive(pw.encode()))

def cells(x):
    if isinstance(x, str):
        yield x
    elif isinstance(x, dict):
        for v in x.values():
            yield from cells(v)
    elif isinstance(x, list):
        for v in x:
            yield from cells(v)

state, bad, feedback, prefs = {}, 0, [], {}
for c in cells(json.load(open(rows_path))):
    c = c.strip()
    if not c.startswith("tpt1."):
        continue
    try:
        _, iv, ct = c.split(".")
        ev = json.loads(aes.decrypt(base64.b64decode(iv), base64.b64decode(ct), None))
        if ev.get("a") == "pref":
            if ev.get("t", 0) >= prefs.get(ev.get("title"), (0, ""))[0]:
                prefs[ev.get("title")] = (ev.get("t", 0), ev.get("note"))
            continue
        if ev.get("a") in ("flag", "note"):
            feedback.append(ev)
            continue
        k = (ev["title"] + "|" + (ev.get("y") or "")).lower()
        if k not in state or ev.get("t", 0) >= state[k].get("t", 0):
            state[k] = {f: str(ev.get(f, ""))[:120] if f != "t" else int(ev.get("t", 0)) for f in ("a", "t", "title", "y", "kind", "where", "link")}
    except Exception:
        bad += 1

os.makedirs(os.path.join(ROOT, "issues", iid), exist_ok=True)
json.dump({"v": state}, open(os.path.join(ROOT, "issues", iid, "screen-state.json"), "w"), ensure_ascii=False)
group = lambda a: sorted(v["title"] + (f" ({v['kind']})" if v["kind"] else "") for v in state.values() if v["a"] == a)
print("SEEN / WATCHES (follow these in 'Your shows', never suggest again):", "; ".join(group("seen")) or "none")
print("MY LIST (tell him when one comes to a Dutch streamer or cinema, never suggest again):", "; ".join(group("list")) or "none")
print("NOT FOR ME (never suggest; steer away from similar):", "; ".join(group("no")) or "none")
import time
later = sorted((v["title"], (time.time() * 1000 - v["t"]) / 86400000) for v in state.values() if v["a"] == "later")
print("NOT SURE (do not suggest again within 30 days; after that it may come back once, with a better reason):",
      "; ".join(f"{t} ({d:.0f} days ago)" for t, d in later) or "none")
print(f"{len(state)} titles, {bad} rows ignored (not decryptable)")

handled_p = os.path.join(ROOT, "kit", "feedback-handled.json")
handled = set(json.load(open(handled_p))) if os.path.exists(handled_p) else set()
todo = [f for f in sorted(feedback, key=lambda f: f.get("t", 0)) if f.get("t") not in handled]
print()
print("PAUL'S FEEDBACK TO ANSWER (Corrections box; then add each t to kit/feedback-handled.json):" if todo else "PAUL'S FEEDBACK: nothing new")
for f in todo:
    if f["a"] == "flag":
        print(f"- t={f['t']} FLAGGED claim {f.get('title')} from issue {f.get('issue')} (we said: {f.get('verdict')}): {f.get('claim')!r}; his note: {f.get('note') or '(none)'}")
    else:
        print(f"- t={f['t']} NOTE from issue {f.get('issue')}: {f.get('note')!r}")

lang = prefs.get("lang", (0, "en"))[1] or "en"
print()
print(f"LANGUAGE: {lang}  (write the whole issue in {'French' if lang == 'fr' else 'English'}, see RUNBOOK 'Language')")
