"""Do-not-repeat digest and claims that fall due, from earlier issues, in one small printout.

Usage:  TPT_PASSWORD=xxxx python kit/history.py <today's issue id>

Replaces "unlock and read the previous issues to check what we already ran". Prints:
  - titles already used for picks, stock of the day, radar, tool of the week, rigging tips, Dutch words, quotes
  - claims whose due date has come and that have no final verdict yet (feed them to parts/checked.json)
"""
import html as _h, json, re, sys
from bs4 import BeautifulSoup
import tptlib

today = sys.argv[1][:10] if len(sys.argv) > 1 else sys.exit("give today's issue id")
cipher = tptlib.aes()
ids = tptlib.previous_ids(sys.argv[1], 60)

WATCH = [("Stock of the day", 30), ("Radar", 30), ("Tool of the week", 30), ("Rigging tip", 60),
         ("Dutch word", 30), ("Quote of the day", 60), ("Lisnard watch", 0)]
clean = lambda el: re.sub(r"\s+", " ", el.get_text(" ")).strip()

picks, found, claims, final = [], {w: [] for w, _ in WATCH}, {}, set()
for n, iid in enumerate(ids):
    src = tptlib.sections_of(iid, cipher)
    if not src:
        continue
    soup = BeautifulSoup(src, "html.parser")
    if n < 30:
        for el in soup.find_all(attrs={"data-pick": True}):
            try:
                picks += [f"{p.get('t')} ({p.get('y', '')})" for p in json.loads(_h.unescape(el["data-pick"]))]
            except Exception:
                pass
    for w, keep in WATCH:
        if not keep or n >= keep:
            continue
        for el in soup.find_all(["div", "section"], class_=re.compile(r"\b(box|fun|brief)\b")):
            head = el.find(["h4", "span"], class_=[None, "lbl"]) or el.find("h4")
            if head and w.lower() in clean(head).lower():
                body = clean(el)[len(clean(head)):].strip()
                found[w].append(f"{iid}: {body[:90]}")
                break
    for s in soup.find_all("script", class_="claims-out"):
        try:
            for c in json.loads(s.string or "[]"):
                claims[c["id"]] = c
        except Exception:
            pass
    for el in soup.find_all(attrs={"data-checked": True}):
        try:
            for c in json.loads(_h.unescape(el["data-checked"])):
                if c.get("verdict") in ("right", "wrong", "partly"):
                    final.add(c["id"])
        except Exception:
            pass

print("PICKS ALREADY SHOWN (last 30 issues, never repeat):", "; ".join(dict.fromkeys(picks)) or "none")
for w, keep in WATCH:
    if keep:
        print(f"\n{w.upper()} (last {keep} issues):")
        print("\n".join("  " + x for x in found[w]) or "  none found")
due = [c for c in claims.values() if c.get("due", "9999") <= today and c["id"] not in final]
print("\nCLAIMS DUE (check each, write verdicts to parts/checked.json):")
print(json.dumps(due, ensure_ascii=False, indent=1) if due else "  none")
