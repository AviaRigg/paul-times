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
# tag balance (9 Nov 2026: three stray </div> in Markets closed #src early, so the phone showed only 5 of 12 pages)
for m in re.finditer(r'<section\b[^>]*data-key="([\w-]+)"[^>]*>(.*?)</section>', src, re.S):
    for tag in ("div", "section", "template", "figure", "table"):
        d = len(re.findall(rf"<{tag}\b", m.group(2))) - len(re.findall(rf"</{tag}>", m.group(2)))
        if d:
            block.append(f"{m.group(1)}: {abs(d)} {'unclosed' if d > 0 else 'extra closing'} <{tag}> (breaks every later page on the phone)")
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
for el in soup.find_all(attrs={"data-checked": True}):
    try:
        if any(re.search(r"https?://", v.get("note", "")) for v in json.loads(_h.unescape(el["data-checked"]))):
            block.append("checked.json notes contain raw URLs (they overflow the phone screen): name the outlet only")
    except Exception:
        pass
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
# layout: the house style of issue No. 1 (15 Oct 2026); these drifted away by the end of October
mast = soup.select_one("section[data-key=front] .mast")
order = [c.get("class", [""])[0] for c in mast.find_all(recursive=False)] if mast else []
if order != ["meta", "name", "motto", "rail"]:
    block.append(f"masthead must be .meta (3 spans: edition and No., Amsterdam · Annecy, date), .name, .motto, .rail (section names); found {order}")
elif len(mast.select(".meta > span")) != 3:
    block.append("masthead .meta needs 3 spans: 'Daily · No. N', 'Amsterdam · Annecy', 'Sun 1 Nov 2026'")
for t in soup.select("section[data-key=front] .teaser"):
    if not "".join(x for x in t.find_all(string=True, recursive=False)).strip():
        block.append("front teaser without its one-line dek (text after the .t headline): " + t.get_text(" ")[:40])
for sec in soup.find_all("section"):
    k = sec.get("data-key")
    kids = [c for c in sec.find_all(recursive=False) if c.name and c.name not in ("template", "script")]
    if k not in ("front",) and not sec.select_one(".opener"):
        block.append(f"{k}: no section opener (big name, 'Section N', tagline); kit/assemble.py adds it, re-run it")
    for i, c in enumerate(kids):
        if "sdk" in (c.get("class") or []) and i <= 3:
            block.append(f"{k}: sudoku sits inside the lead story (block {i}); puzzles go between stories")
for d in soup.select(".tl .d"):
    txt = d.get_text(" ").strip()
    if not txt or len(txt) > 9:
        block.append(f"week timeline date label must be short like 'Sun 1' or '12 Nov' (found {txt!r}); put times in the text")
        break
if soup.select_one("section[data-key=week] ol.tl") is None:
    block.append("week: missing the ol.tl timeline")
if not soup.select(".pull"):
    notes.append("no pull quote anywhere (issue No. 1 had 2 or more)")
if not soup.select_one(".sources"):
    notes.append("back: no .sources box (issue No. 1 style: div.sources.blk with a kicker and one <p><b>Section:</b> links</p> per section)")
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

# images are mandatory (Paul's rule, 31 Oct 2026: the front shipped with a data-wiki file photo that never showed)
front = soup.find("section", attrs={"data-key": "front"})
if front is not None:
    live = [f for f in front.select("figure.photo[data-src]") if f["data-src"] not in dead]
    if not live:
        block.append("front: no verified news photo. The front lead needs a figure.photo with data-src (curl 200) "
                     "from a news article; a data-wiki file photo alone is not enough")
for sec in soup.find_all("section"):
    k = sec.get("data-key")
    if k in ("front", "week", "back"):
        continue
    if not [f for f in sec.select("figure.photo, figure.poster") if f.get("data-src") not in dead or f.get("data-wiki")]:
        block.append(f"{k}: no photo at all (every section lead needs a real photo)")
    elif not [f for f in sec.select("figure.photo[data-src]") if f["data-src"] not in dead]:
        notes.append(f"{k}: only file photos (data-wiki); find a real news photo with data-src")

# no empty pages (Paul's rule, 11 Nov 2026: Local shipped with "no verified local headline yet")
EMPTY = re.compile(r"no verified (local )?(headline|news|story)|nothing (new )?(was )?found|more later today|still being written", re.I)
MIN_STORIES = {"local": 5}
for sec in soup.find_all("section"):
    k = sec.get("data-key")
    if k in ("front", "week", "back"):
        continue
    stories = [h for h in sec.select(".head h3, .head h4, .brief h4, .box h4") if not h.find_parent(attrs={"data-wx": True})]
    need = MIN_STORIES.get(k, 2)
    if len(stories) < need:
        block.append(f"{k}: only {len(stories)} stories (need {need}); no page may be empty or thin. "
                     + ("Local fallback: ODS Radio (odsradio.com/news/locales), Le Dauphiné Libéré Annecy, Le Messager, France 3 Alpes" if k == "local" else "research more"))
    lead = sec.select_one(".head h3, .head h4, .brief h4")
    if lead is not None and EMPTY.search(lead.get_text(" ")):
        block.append(f"{k}: the lead headline admits there is no news ('{lead.get_text(' ', strip=True)[:60]}'); find real stories")

print("BLOCKING:" if block else "no blocking problems")
for b in block:
    print("  ! " + b)
print("NOTES:")
for n in notes:
    print("  " + n)
sys.exit(1 if block else 0)
