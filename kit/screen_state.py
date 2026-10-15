"""Turn Paul's encrypted taps (Google Sheet rows from his "Paul Times taps" form) into the state the paper uses.

Usage:  TPT_PASSWORD=xxxx python kit/screen_state.py rows.json <issue id>
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

state, bad = {}, 0
for c in cells(json.load(open(rows_path))):
    c = c.strip()
    if not c.startswith("tpt1."):
        continue
    try:
        _, iv, ct = c.split(".")
        ev = json.loads(aes.decrypt(base64.b64decode(iv), base64.b64decode(ct), None))
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
