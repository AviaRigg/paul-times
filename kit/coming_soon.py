"""Persistent "Coming soon" list for the Screen page (Paul's rule, 11 Nov 2026).

Once a film or series enters Coming soon it STAYS in every issue until its release date has passed;
new titles are added, nothing drops out early. The list lives in kit/coming-soon.json (committed: it
holds only public film data) and kit/assemble.py renders the whole list on every build.

How it works in kit/assemble.py (call render_into(screen_html, issue_date)):
  1. Every <figure class="poster"> in the agent's <div class="pgrid"> (if any) and every object in
     parts/coming-soon.json is merged into the store by title: new titles are added, known titles get
     their non-empty fields updated (date, trailer id, poster, where...). Nothing is ever removed here.
  2. Titles whose release date is before the issue date are dropped (a film stays on its release day).
     Dates: data-date="YYYY-MM-DD" (best), "YYYY-MM" (drops after that month), "YYYY" (after that year);
     without data-date the figcaption label is parsed ("25 Nov", "Dec", "Spring 2027" -> kept, undated).
     Undated titles are kept and sorted last.
  3. The agent's pgrid (or a <!--COMING--> marker) is replaced by the full sorted list. If the agent
     wrote neither, the list is inserted with its own "Coming soon" head before <!--PICKS-->.
Usage for checks:  python kit/coming_soon.py [issue id]   (prints the list that issue would show)
"""
import calendar, datetime as dt, html as _h, json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STORE = os.path.join(ROOT, "kit", "coming-soon.json")
MONTHS = {m.lower(): i for i, m in enumerate(calendar.month_abbr) if m}
MONTHS.update({m.lower(): i for i, m in enumerate(calendar.month_name) if m})
MONTHS.update({"janv": 1, "févr": 2, "fevr": 2, "mars": 3, "avr": 4, "mai": 5, "juin": 6, "juil": 7, "août": 8,
               "aout": 8, "sept": 9, "déc": 12, "dec": 12})


def key(t):
    return re.sub(r"[^a-z0-9]", "", (t or "").lower())


def load():
    try:
        return json.load(open(STORE, encoding="utf-8"))
    except (OSError, ValueError):
        return []


def save(items):
    json.dump(items, open(STORE, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    open(STORE, "a").write("\n")


def guess_date(label, today):
    """'25 Nov' -> 'YYYY-11-25', 'Dec' -> 'YYYY-12', '2027' -> '2027'; year rolls forward when the month is past."""
    s = (label or "").strip().lower().replace(".", "")
    y = re.search(r"\b(20\d\d)\b", s)
    year = int(y.group(1)) if y else None
    d = re.search(r"\b(\d{1,2})\b(?!\d)", re.sub(r"20\d\d", "", s))
    mon = next((v for k, v in MONTHS.items() if re.search(r"\b" + re.escape(k), s)), None)
    if mon:
        if year is None:
            year = today.year + (1 if mon < today.month else 0)
        if d:
            try:
                return dt.date(year, mon, int(d.group(1))).isoformat()
            except ValueError:
                pass
        return f"{year:04d}-{mon:02d}"
    return f"{year:04d}" if year else ""


def last_day(date_s):
    """Last day a title with this date is still 'coming' (inclusive)."""
    try:
        if re.fullmatch(r"\d{4}-\d\d-\d\d", date_s):
            return dt.date.fromisoformat(date_s)
        if re.fullmatch(r"\d{4}-\d\d", date_s):
            y, m = map(int, date_s.split("-"))
            return dt.date(y, m, calendar.monthrange(y, m)[1])
        if re.fullmatch(r"\d{4}", date_s):
            return dt.date(int(date_s), 12, 31)
    except ValueError:
        pass
    return None


def from_figures(fragment, today):
    from bs4 import BeautifulSoup
    out = []
    for f in BeautifulSoup(fragment, "html.parser").select("figure.poster"):
        a = {k: (" ".join(v) if isinstance(v, list) else v) for k, v in f.attrs.items() if k != "class"}
        cap = f.find("figcaption")
        label = cap.b.get_text(strip=True) if cap and cap.b else ""
        title = a.get("data-t") or (cap.get_text(" ", strip=True)[len(label):].strip() if cap else "")
        if not title:
            continue
        a["data-t"] = title
        out.append({"t": title, "label": label, "date": a.pop("data-date", "") or guess_date(label, today), "attrs": a})
    return out


def merge(store, new, today):
    idx = {key(x["t"]): x for x in store}
    for n in new:
        k = key(n["t"])
        if k in idx:
            old = idx[k]
            nd, od = n.get("date", ""), old.get("date", "")
            # never trade a precise date for a vaguer one ("Dec" must not overwrite "18 Dec")
            if nd and not (od and len(nd) < len(od) and od.startswith(nd)):
                old["date"] = nd
                if n.get("label"):
                    old["label"] = n["label"]
            old.setdefault("attrs", {}).update({a: v for a, v in (n.get("attrs") or {}).items() if v})
        else:
            n = {"t": n["t"], "label": n.get("label", ""), "date": n.get("date", ""), "attrs": n.get("attrs") or {},
                 "added": today.isoformat()}
            n["attrs"].setdefault("data-t", n["t"])
            store.append(n)
            idx[k] = n
    return store


RELEASED = re.compile(r"\b(in cinemas|out now|now (in|on|streaming)|streaming now|released|en salles)\b", re.I)


def live(store, today):
    keep = [x for x in store if (last_day(x.get("date", "")) or dt.date.max) >= today
            and not (not x.get("date") and RELEASED.search(x.get("label", "")))]
    return sorted(keep, key=lambda x: (last_day(x.get("date", "")) or dt.date.max, x.get("date", ""), x["t"].lower()))


def render(items):
    figs = []
    for x in items:
        a = dict(x.get("attrs") or {})
        a["data-t"] = x["t"]
        if x.get("date"):
            a["data-date"] = x["date"]
        attrs = "".join(f' {k}="{_h.escape(str(v), quote=True)}"' for k, v in a.items())
        figs.append(f'<figure class="poster"{attrs}><figcaption><b>{_h.escape(x.get("label") or "TBA")}</b>{_h.escape(x["t"])}</figcaption></figure>')
    return '<div class="pgrid blk">\n' + "\n".join(figs) + "\n</div>"


PGRID = re.compile(r'<div class="pgrid[^"]*"[^>]*>.*?</figure>\s*</div>', re.S)


def render_into(screen, today, extra=None, write=True):
    """Merge the agent's posters (and extra objects) into the store and put the full list into screen.html."""
    m = PGRID.search(screen)
    new = from_figures(m.group(0), today) if m else []
    for e in extra or []:
        if e.get("t"):
            new.append({"t": e["t"], "label": e.get("label", ""), "date": e.get("date") or guess_date(e.get("label", ""), today),
                        "attrs": e.get("attrs") or {}})
    store = merge(load(), new, today)
    items = live(store, today)
    if write:
        save(items)  # released titles leave the store for good
    if not items:
        return screen.replace("<!--COMING-->", ""), 0
    grid = render(items)
    if m:
        screen = screen[:m.start()] + grid + screen[m.end():]
    elif "<!--COMING-->" in screen:
        screen = screen.replace("<!--COMING-->", grid, 1)
    else:
        block = '<div class="head blk kn"><div class="kicker">Coming soon</div><h4>Cinemas and streaming</h4></div>\n' + grid + "\n"
        screen = screen.replace("<!--PICKS-->", block + "<!--PICKS-->", 1) if "<!--PICKS-->" in screen else screen + "\n" + block
    return screen, len(items)


if __name__ == "__main__":
    today = dt.date.fromisoformat(sys.argv[1]) if len(sys.argv) > 1 else dt.date.today()
    for x in live(load(), today):
        print(f'{x.get("date") or "undated":10}  {x.get("label",""):10}  {x["t"]}  yt={x.get("attrs", {}).get("data-yt", "-")}  added {x.get("added", "?")}')
