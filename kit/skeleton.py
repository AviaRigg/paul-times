"""Print the STRUCTURE of an earlier issue (tags, classes, attribute names, a few words of text), not its content.

Usage:  TPT_PASSWORD=xxxx python kit/skeleton.py [<issue id>]      (default: the latest issue in docs/issues.json)

This replaces reading the whole previous sections.html (about 35k tokens) as a pattern: the skeleton is a few KB.
Repeated identical blocks collapse into "xN". Also prints the issue number to continue from.
"""
import re, sys
from bs4 import BeautifulSoup
import tptlib

iid = sys.argv[1] if len(sys.argv) > 1 else (tptlib.index() or [{}])[0].get("id")
src = tptlib.sections_of(iid) if iid else None
if not src:
    sys.exit("no earlier issue source found: build from BLOCKS.md instead")
soup = BeautifulSoup(src, "html.parser")


def sig(el):
    cls = ".".join(el.get("class", []))
    data = [a for a in el.attrs if a.startswith("data-")]
    return el.name + ("." + cls if cls else "") + ("".join(" [%s]" % a for a in data))


def words(el, n=34):
    t = re.sub(r"\s+", " ", el.get_text(" ")).strip()
    return (t[:n] + "…") if len(t) > n else t


def line(el, depth):
    pad = "  " * depth
    kids = [c for c in el.find_all(recursive=False) if c.name != "template"]
    inner = ""
    if el.name != "p" and kids and depth < 2:
        inner = "  ⊃ " + " ".join(sorted({sig(c).split(" ")[0] for c in kids}))[:90]
    more = " +more" if el.find("template", class_="more") else ""
    return f'{pad}{sig(el)}{more}  "{words(el)}"{inner}'


m = re.search(r"No\.\s*(\d+)", src)
print(f"# skeleton of {iid}; issue number {m.group(1) if m else '?'}; next number {int(m.group(1)) + 1 if m else '?'}")
for sec in soup.find_all("section"):
    print(f"\n<section data-key={sec.get('data-key')} data-title={sec.get('data-title')!r} data-accent={sec.get('data-accent')}>")
    prev, run = None, 0
    for el in sec.find_all(recursive=False):
        s = sig(el)
        if s == prev:
            run += 1
            continue
        if run:
            print(f"  … x{run + 1} of the above")
        prev, run = s, 0
        print(line(el, 1))
    if run:
        print(f"  … x{run + 1} of the above")
tail = soup.find_all("script", class_="claims-out")
print(f"\n# claims-out scripts: {len(tail)}")
