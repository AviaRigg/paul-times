"""Check (and optionally repair) issues/<id>/sections.html before building. One call replaces many small checks.

Usage:  python kit/lint.py <issue id> [--fix] [--no-net]

Blocking problems exit with code 1: missing sections, a brief or big story without its tap-for-more template,
broken data-pick / data-checked JSON, missing back-page pieces.
Everything else is a report. With --fix: dead image links (403/404/410) lose their image (the wiki fallback stays if
there is one), dead Apply links are removed, em and en dashes are rewritten. Unreachable hosts (timeouts, blocked
network) are kept, as the runbook says. URL checks run in parallel.
"""
import concurrent.futures as cf, html as _h, json, os, re, sys, urllib.request, urllib.error
from bs4 import BeautifulSoup
import tptlib

iid = sys.argv[1]
fix, net = "--fix" in sys.argv, "--no-net" not in sys.argv
path = os.path.join(tptlib.ROOT, "issues", iid, "sections.html")
src = open(path, encoding="utf-8").read()
soup = BeautifulSoup(src, "html.parser")
block, notes = [], []

# structure
keys = [s.get("data-key") for s in soup.find_all("section")]
want = ["front", "world", "france", "local", "markets", "crypto", "tech", "craft", "sport", "screen", "week", "back"]
miss = [k for k in want if k not in keys]
if miss:
    block.append("missing sections: " + ", ".join(miss))
for sec in soup.find_all("section"):
    k = sec.get("data-key")
    nb = [b.find("h4").get_text(" ").strip()[:50] if b.find("h4") else "?" for b in sec.select(".brief") if not b.find("template", class_="more")]
    if nb:
        block.append(f"{k}: {len(nb)} brief(s) without a 'more' template: " + "; ".join(nb[:6]) + (" ..." if len(nb) > 6 else ""))
    nh = [h.get_text(" ").strip()[:50] for h in sec.select(".head") if not h.find("template", class_="more") and not h.get("data-more")]
    if nh:
        notes.append(f"{k}: {len(nh)} head(s) without 'more' (fine for portfolio, editorial and lists; check real stories): " + "; ".join(nh[:4]))
    if sec.find("template", class_="more") is None and k not in ("front", "back", "week"):
        notes.append(f"{k}: no tap-for-more templates at all")
for a in ("pick", "checked"):
    for el in soup.find_all(attrs={"data-" + a: True}):
        try:
            json.loads(_h.unescape(el["data-" + a]))
        except Exception as e:
            block.append(f"data-{a} JSON broken: {e}")
need = {"[data-feedback]": "feedback box", "[data-sudoku]": "sudoku", "[data-wx]": "live weather box"}
for sel, name in need.items():
    if not soup.select(sel):
        block.append("missing " + name)
if not soup.find("a", href="./?archive"):
    block.append("missing the 'Past issues' link to ./?archive")
if not soup.find("script", class_="claims-out"):
    notes.append("no claims-out script (3 to 6 claims expected)")
if soup.find(attrs={"style": True}) or soup.find("style"):
    notes.append("inline style found (use the building blocks)")

# visuals
figs = soup.select("figure.photo, figure.poster")
notes.append(f"{len(soup.select('figure.photo'))} photos, {len(soup.select('figure.poster'))} posters, "
             f"{len(soup.select('.brief'))} briefs, {len(soup.select('template.more'))} 'more' templates, {len(soup.select('[data-sudoku]'))} sudokus")
nt = [p.get("data-t", "?") for p in soup.select("figure.poster") if not p.get("data-yt")]
if nt:
    notes.append(f"posters without trailer id ({len(nt)}): " + ", ".join(nt[:8]))
for el in soup.find_all(attrs={"data-pick": True}):
    try:
        np_ = [p.get("t") for p in json.loads(_h.unescape(el["data-pick"])) if not p.get("yt")]
        if np_:
            notes.append("picks without trailer id: " + ", ".join(np_))
    except Exception:
        pass

# urls
urls = {}
for f in soup.select("figure[data-src]"):
    urls.setdefault(f["data-src"], []).append("img")
for a in soup.select("a.apply[href]"):
    urls.setdefault(a["href"], []).append("apply")


def status(u):
    try:
        r = urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0", "Range": "bytes=0-0"})
        with urllib.request.urlopen(r, timeout=12) as x:
            return x.status
    except urllib.error.HTTPError as e:
        return e.code
    except Exception:
        return 0


dead = []
if net and urls:
    with cf.ThreadPoolExecutor(16) as ex:
        res = dict(zip(urls, ex.map(status, urls)))
    dead = [u for u, s in res.items() if s in (403, 404, 410)]
    unk = sum(1 for s in res.values() if s == 0)
    notes.append(f"checked {len(urls)} urls: {len(urls) - len(dead) - unk} ok, {len(dead)} dead, {unk} unreachable (kept)")
    for u in dead:
        notes.append(f"  DEAD {res[u]} {'/'.join(urls[u])}: {u[:100]}")

if fix:
    txt = src
    for u in dead:
        e = re.escape(u)
        txt = re.sub(rf'(<figure[^>]*?)\sdata-src="{e}"([^>]*data-wiki=)', r"\1\2", txt)
        txt = re.sub(rf'<figure[^>]*data-src="{e}"[^>]*>.*?</figure>', "", txt, flags=re.S)
        txt = re.sub(rf'<a class="apply" href="{e}">[^<]*</a>', "", txt)
    txt = re.sub(r"\s—\s", ", ", txt).replace("—", ", ")
    txt = re.sub(r"(?<=\d)–(?=\d)", "-", txt).replace(" – ", ", ").replace("–", "-")
    if txt != src:
        open(path, "w", encoding="utf-8").write(txt)
        notes.append("--fix: rewrote the file (dead links removed, dashes fixed)")
elif re.search("[—–]", src):
    notes.append("em or en dashes present (run with --fix)")

print("BLOCKING:" if block else "no blocking problems")
for b in block:
    print("  ! " + b)
print("NOTES:")
for n in notes:
    print("  " + n)
sys.exit(1 if block else 0)
