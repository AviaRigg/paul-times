"""Assemble issues/<id>/sections.html from the part files the research agents and the editor wrote.

Usage:  python kit/assemble.py <issue id> [--edition daily|sunday]

Reads issues/<id>/parts/:
  front.html world.html france.html local.html markets.html crypto.html tech.html craft.html sport.html
  screen.html [sunday.html] week.html back.html          (a part may be bare blocks or a full <section>)
  meta.json     {"title": "lead headline", "sudoku": "Medium:32,Hard:25"}   (title is optional here)
  picks.json    list of Tonight's-pick objects, replaces <!--PICKS--> in screen.html (escaping handled here)
  checked.json  list of verdicts, replaces <!--CHECKED--> in back.html
  claims.json   list of claims, written as the claims-out script at the end
  tip.html      rigging tip blocks, replaces <!--TIP--> in back.html
Placeholders usable in any part: {{NO}} (issue number) {{DATE}} {{WEEKDAY}} {{EDITION}}
Missing parts become a short "more later today" section, so a partial issue can be shipped early.
Sudokus are placed in random sections (seeded by the id, so rebuilds are stable), never two in one section.
"""
import datetime as dt, html as _h, json, os, random, re, sys
from html.parser import HTMLParser
import tptlib

ROOT = tptlib.ROOT
iid = sys.argv[1]
edition = "sunday" if "--edition" in sys.argv and sys.argv[sys.argv.index("--edition") + 1] == "sunday" else "daily"
parts = os.path.join(ROOT, "issues", iid, "parts")
date = dt.date.fromisoformat(iid[:10])

ORDER = [("front", "Front page", "--a-front"), ("world", "The World", "--a-world"), ("france", "France", "--a-france"),
         ("local", "Local", "--a-local"), ("markets", "Markets", "--a-markets"), ("crypto", "Crypto", "--a-crypto"),
         ("tech", "Tech and AI", "--a-tech"), ("craft", "The Craft", "--a-craft"), ("sport", "Sport", "--a-sport"),
         ("screen", "Screen", "--a-screen"), ("sunday", "The Sunday Read", "--a-week"),
         ("week", "The Week Ahead", "--a-week"), ("back", "Tip and Sources", "--a-back")]
# Section openers, as in issue No. 1 (15 Oct 2026): big name, "Section N", italic tagline.
# Added automatically when a part has none, so the layout cannot drift again.
OPENERS = {"world": ("The World", "The lead story, then the smaller ones you should still know"),
           "france": ("France", "Politics in Paris: the budget, the street and the race for 2027"),
           "local": ("Local", "Annecy, Haute-Savoie and the weather where you ride"),
           "markets": ("Markets", "Yesterday's close, the story behind it, and your portfolio"),
           "crypto": ("Crypto", "Coins, stablecoins, CBDCs and the rules around them"),
           "tech": ("Tech and AI", "Models, chips and the patch you need tonight"),
           "craft": ("The Craft", "3D, rigging, software, games and your next job"),
           "sport": ("Sport", "Formula 1 · Tennis · Les Bleus"),
           "screen": ("Screen", "Films, series, scores and tonight's pick"),
           "sunday": ("The Sunday Read", "Long reads for a slow morning"),
           "week": ("The Week Ahead", "Your calendar, our opinion and a harder puzzle"),
           "back": ("Back Page", "A tip for tonight, and where today's facts came from")}
if edition != "sunday":
    ORDER = [o for o in ORDER if o[0] != "sunday"]


def rd(name):
    p = os.path.join(parts, name)
    return open(p, encoding="utf-8").read() if os.path.exists(p) else None


def rj(name, default):
    t = rd(name)
    return json.loads(t) if t else default


def attr(obj):  # JSON into a single-quoted HTML attribute
    return json.dumps(obj, ensure_ascii=False).replace("&", "&amp;").replace("<", "&lt;").replace("'", "&#39;")


prev = [int(i["no"]) for i in tptlib.index() if i.get("no") and i["id"] < iid]
no = (max(prev) + 1) if prev else 1
meta = rj("meta.json", {})
subs = {"{{NO}}": str(no), "{{DATE}}": f"{date.day} {date.strftime('%B %Y')}", "{{WEEKDAY}}": date.strftime("%A"),
        "{{EDITION}}": "Sunday" if edition == "sunday" else "Daily"}


class TopLevel(HTMLParser):
    """Offsets just after each top-level element of a fragment."""
    VOID = {"img", "br", "hr", "input", "meta", "link", "source", "area", "base", "col", "embed", "wbr"}

    def __init__(self, text):
        super().__init__(convert_charrefs=False)
        self.text, self.depth, self.ends = text, 0, []
        self.lines = [0]
        for m in re.finditer("\n", text):
            self.lines.append(m.end())
        self.feed(text)

    def off(self):
        l, c = self.getpos()
        return self.lines[l - 1] + c

    def handle_starttag(self, tag, attrs):
        if tag not in self.VOID:
            self.depth += 1

    def handle_startendtag(self, tag, attrs):
        pass

    def handle_endtag(self, tag):
        if tag in self.VOID:
            return
        self.depth -= 1
        if self.depth == 0:
            self.ends.append(self.off() + len(tag) + 3)


BREAK = re.compile(r'\s*<(?:div|figure|ol|p)\b[^>]*class="([^"]*)"')


def sudoku_break(t, rnd):
    """A block break BETWEEN stories, never inside the lead story (issue No. 1 put puzzles after a story or at the end).
    Valid: just before a .brief, .head or .box that comes after the section's first story is over."""
    ends = TopLevel(t).ends
    nxt = [(e, (BREAK.match(t, e) or [None, ""])[1]) for e in ends]
    seen_story, cands = False, []
    for i, (e, cls) in enumerate(nxt):
        c = cls.split()
        starts_story = any(x in c for x in ("brief", "head", "box", "pick", "mylist"))
        if starts_story and seen_story and i >= 3:
            cands.append(e)
        if i >= 1:
            seen_story = True
    if not cands:
        return ends[-1] if ends else len(t)
    return rnd.choice(cands[len(cands) // 3:] or cands)


def opener(key, no_):
    name, tag = OPENERS[key]
    return (f'<div class="blk kn"><div class="opener"><span class="n">{no_}</span><h2>{_h.escape(name)}</h2></div>'
            f'<p class="tagline">{_h.escape(tag)}</p></div>\n')


out, used_sections, missing = [], [], []
sudoku_n = len([x for x in (meta.get("sudoku") or ("Easy:38,Medium:32,Hard:26,Hard:24" if edition == "sunday" else "Medium:32,Hard:25")).split(",") if x])
bodies = {}
for key, title, accent in ORDER:
    t = rd(key + ".html")
    if t is None:
        missing.append(key)
        t = (f'<div class="brief blk"><div class="kicker">{title}</div><h4>More later today</h4>'
             f"<p>This section is still being written. It will appear in a later update of today's issue.</p></div>")
    for k, v in subs.items():
        t = t.replace(k, v)
    if key == "screen":
        picks = rj("picks.json", None)
        if picks is not None:
            t = t.replace("<!--PICKS-->", f"<div class=\"pick blk\" data-pick='{attr(picks)}'></div><div class=\"mylist blk\" data-mylist></div>")
    if key == "back":
        t = t.replace("<!--CHECKED-->", f"<div class=\"checked blk\" data-checked='{attr(rj('checked.json', []))}'></div>" if rd("checked.json") else "")
        t = t.replace("<!--TIP-->", rd("tip.html") or "")
    bodies[key] = (title, accent, t)

# section openers (number = position in the paper; front has the masthead instead)
for pos, key in enumerate(bodies, start=1):
    if key in OPENERS and 'class="opener"' not in bodies[key][2]:
        title, accent, t = bodies[key]
        bodies[key] = (title, accent, opener(key, pos) + t.lstrip())

# sudoku: honour markers already present, add the missing ones in random distinct sections at block breaks
present = {int(m) for b in bodies.values() for m in re.findall(r'data-sudoku="(\d+)"', b[2])}
rnd = random.Random(int(re.sub(r"\D", "", iid)[:8]))
pool = [k for k in bodies if k not in ("front", "back") and not re.search(r'data-sudoku="', bodies[k][2]) and k not in missing]
for n in range(sudoku_n):
    if n in present or not pool:
        continue
    k = rnd.choice(pool)
    pool.remove(k)
    title, accent, t = bodies[k]
    at = sudoku_break(t, rnd)
    bodies[k] = (title, accent, t[:at] + f'\n<div class="sdk blk" data-sudoku="{n}"></div>' + t[at:])

for key, (title, accent, t) in bodies.items():
    if re.match(r"\s*<section\b", t):
        out.append(t.strip())
    else:
        out.append(f'<section data-key="{key}" data-title="{_h.escape(meta.get("titles", {}).get(key, title))}" data-accent="{accent}">\n{t.strip()}\n</section>')

claims = rj("claims.json", [])
if claims:
    out.append('<script type="application/json" class="claims-out">' + json.dumps(claims, ensure_ascii=False).replace("</", "<\\/") + "</script>")
dest = os.path.join(ROOT, "issues", iid, "sections.html")
open(dest, "w", encoding="utf-8").write("\n".join(out) + "\n")
print(f"assembled {iid} ({edition}), issue No. {no}, {len(bodies)} sections, {sum(len(x) for x in out) // 1024} KB"
      + (f"; MISSING parts (placeholders used): {', '.join(missing)}" if missing else "") + "; sudokus: " + str(sudoku_n))
