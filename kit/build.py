"""Build and encrypt one issue of The Paul Times.

Usage:  TPT_PASSWORD=xxxx python kit/build.py 2026-10-15 [--edition daily|weekly] [--title "Lead headline"] [--sudoku Medium:32,Hard:25]

Reads   issues/<id>/sections.html (+ charts.json, + any PNGs it references)
Writes  docs/issues/<id>.enc, updates docs/issues.json, and a plain preview at build/<id>.html (gitignored).
<id> is the date for dailies, <date>-weekly for weeklies.
"""
import argparse, base64, datetime as dt, json, os, re, subprocess, sys
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KIT = os.path.join(ROOT, "kit")
sys.path.insert(0, KIT)
import sudoku  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("id")
ap.add_argument("--edition", default="daily")
ap.add_argument("--title", default="")
ap.add_argument("--sudoku", default="Medium:32,Hard:25")
a = ap.parse_args()

folder = os.path.join(ROOT, "issues", a.id)
date = dt.date.fromisoformat(a.id[:10])
label = ("Weekly · " if a.edition == "weekly" else "") + date.strftime("%a %d %b %Y")

# charts
if os.path.exists(os.path.join(folder, "charts.json")):
    subprocess.run([sys.executable, os.path.join(KIT, "charts.py"), folder], check=True)

# sudoku, seeded by issue id so a rebuild gives the same puzzles
seed = int(re.sub(r"\D", "", a.id)[:8])
puzzles = []
for n, part in enumerate(a.sudoku.split(",")):
    lab, clues = part.split(":")
    p, s, f = sudoku.make(int(clues), seed + n)
    puzzles.append({"label": lab, "puzzle": p, "solution": s})

sections = open(os.path.join(folder, "sections.html"), encoding="utf-8").read()

def inline(m):
    name = m.group(1)
    path = os.path.join(folder, name)
    if not os.path.exists(path):
        print("WARNING missing image", name)
        return m.group(0)
    w, h = Image.open(path).size
    b64 = base64.b64encode(open(path, "rb").read()).decode()
    return f'src="data:image/png;base64,{b64}" width="{w}" height="{h}"'

sections = re.sub(r'src="([^"/:]+\.png)"(?:\s+width="\d+"\s+height="\d+")?', inline, sections)
tpl = open(os.path.join(KIT, "template.html"), encoding="utf-8").read()
html = (tpl.replace("{{SECTIONS}}", sections).replace("{{SUDOKU_DATA}}", json.dumps(puzzles))
        .replace("{{ISSUE_ID}}", a.id).replace("{{ISSUE_LABEL}}", label))
if "—" in html:
    print("WARNING: em dash found in issue text")
os.makedirs(os.path.join(ROOT, "build"), exist_ok=True)
open(os.path.join(ROOT, "build", a.id + ".html"), "w", encoding="utf-8").write(html)

# encrypt
pw = os.environ.get("TPT_PASSWORD")
if not pw:
    sys.exit("Set TPT_PASSWORD")
cfg = json.load(open(os.path.join(ROOT, "docs", "crypto.json")))
salt = base64.b64decode(cfg["salt"])
key = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=cfg["iterations"]).derive(pw.encode())
iv = os.urandom(12)
ct = AESGCM(key).encrypt(iv, html.encode("utf-8"), None)
os.makedirs(os.path.join(ROOT, "docs", "issues"), exist_ok=True)
json.dump({"v": 1, "iv": base64.b64encode(iv).decode(), "ct": base64.b64encode(ct).decode()},
          open(os.path.join(ROOT, "docs", "issues", a.id + ".enc"), "w"))

idx_path = os.path.join(ROOT, "docs", "issues.json")
idx = json.load(open(idx_path)) if os.path.exists(idx_path) else []
idx = [i for i in idx if i["id"] != a.id]
idx.append({"id": a.id, "date": date.isoformat(), "edition": a.edition, "title": a.title})
idx.sort(key=lambda i: (i["date"], i["edition"] == "weekly"), reverse=True)
json.dump(idx, open(idx_path, "w"), indent=1)
print("built", a.id, f"{len(html)//1024} KB", "->", "docs/issues/" + a.id + ".enc")
