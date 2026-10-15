"""Render The Paul Times charts from an issue's charts.json into PNGs in the same folder.

Usage: python kit/charts.py issues/2026-10-15

charts.json is a list of chart specs. Every spec has "type" and "file" (output PNG name).
Types:
  bars     signed horizontal bars      {"items": [["S&P 500", -1.11], ...], "unit": "%"}
  targets  weight vs target bars       {"items": [["EQQB", 37.6, 15], ...]}
  line     dated line                  {"points": [["2026-09-14", 76.8], ...], "fmt": "{:.1f}k",
                                         "ref": {"value": 113.1, "label": "a year ago: 113.1k"}}
  rank     plain ranking bars          {"items": [["Nvidia", 5.33], ...], "highlight": "Apple",
                                         "ref": {"value": 5, "label": "5 trillion"}, "fmt": "{:.2f}"}
  map      locator map                 {"bbox": [x0, x1, y0, y1], "aspect": 1.1, "size": [4.6, 3.6],
                                         "highlight": {"Saudi Arabia": "#d9cfb8"},
                                         "points": [{"lon": 46.7, "lat": 24.7, "label": "RIYADH", "dx": 0.5, "dy": 0.6,
                                                     "ha": "left", "black": false, "bold": true}],
                                         "arrow": {"from": [44.2, 15.4], "to": [46.7, 24.7], "rad": -0.25,
                                                   "label": "about 1,070 km", "at": [42.2, 20.6]},
                                         "labels": [["YEMEN", 48.2, 15.8]], "water": [["Red Sea", 38.5, 18.5, -55]]}
  track    F1 circuit layout           {"circuit": "us-2012", "start_label": "Start / finish"}
             circuit ids: github.com/bacinger/f1-circuits (circuits/<id>.geojson)
Accent colour per chart: optional "accent" (hex).
"""
import json, math, os, sys, datetime as dt, urllib.request
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as md
import matplotlib.patheffects as pe
from matplotlib import font_manager as fm
from matplotlib.patches import Polygon, FancyArrowPatch

KIT = os.path.dirname(os.path.abspath(__file__))
fm.fontManager.addfont(os.path.join(KIT, "fonts", "SourceSerif.ttf"))
SERIF = fm.FontProperties(fname=os.path.join(KIT, "fonts", "SourceSerif.ttf")).get_name()
plt.rcParams.update({"font.family": SERIF, "font.size": 8, "axes.edgecolor": "#111", "axes.linewidth": 0.6})
INK, RED, GREEN, TAN = "#111111", "#8a1c1c", "#1d6b2f", "#d9cfb8"
HALO = [pe.withStroke(linewidth=2.2, foreground="white")]
DPI = 300


def off(ax):
    for s in ax.spines.values():
        s.set_visible(False)


def save(fig, out):
    fig.savefig(out, dpi=DPI, bbox_inches="tight", pad_inches=0.03, facecolor="white")
    plt.close(fig)


def bars(c, out):
    items = c["items"]; unit = c.get("unit", "%")
    fig, ax = plt.subplots(figsize=(3.3, 0.32 * len(items) + 0.2))
    names = [i[0] for i in items]; vals = [i[1] for i in items]
    ax.barh(names, vals, color=[RED if v < 0 else GREEN for v in vals], height=0.6)
    span = max(abs(v) for v in vals) or 1
    for i, v in enumerate(vals):
        ax.text(v + (span * 0.03 if v >= 0 else -span * 0.03), i, f"{v:+.2f}{unit}", va="center",
                ha="left" if v >= 0 else "right", fontsize=7)
    lo = min(0, min(vals)); hi = max(0, max(vals))
    ax.set_xlim(lo - span * 0.45, hi + span * 0.45); ax.axvline(0, color=INK, lw=0.6)
    ax.set_xticks([]); off(ax); ax.tick_params(left=False, labelsize=7.2)
    save(fig, out)


def targets(c, out):
    rows = c["items"]
    fig, ax = plt.subplots(figsize=(3.3, 0.27 * len(rows) + 0.2))
    top = max(max(r[1], r[2]) for r in rows) * 1.18
    ax.barh(range(len(rows)), [r[1] for r in rows], height=0.55, color=[RED if r[1] > r[2] + 3 else INK for r in rows])
    for i, r in enumerate(rows):
        ax.plot([r[2], r[2]], [i - 0.4, i + 0.4], color=GREEN, lw=2)
        ax.text(max(r[1], r[2]) + top * 0.02, i, f"{r[1]:.1f}%", va="center", fontsize=6.8)
    ax.set_yticks(range(len(rows))); ax.set_yticklabels([r[0] for r in rows], fontsize=7.2); ax.invert_yaxis()
    ax.set_xticks([]); ax.set_xlim(0, top); off(ax); ax.tick_params(left=False)
    ax.text(top, len(rows) - 0.1, "bar = actual weight   green tick = your target", fontsize=6, ha="right", style="italic", color="#444")
    save(fig, out)


def line(c, out):
    acc = c.get("accent", RED); fmt = c.get("fmt", "{:.1f}")
    pts = [(dt.date.fromisoformat(d), v) for d, v in c["points"]]
    xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
    fig, ax = plt.subplots(figsize=(3.3, 1.6))
    ax.plot(xs, ys, color=INK, lw=1.1, marker="o", ms=3.5)
    ax.plot(xs[-1], ys[-1], "o", color=acc, ms=5.5)
    vals = ys + ([c["ref"]["value"]] if c.get("ref") else [])
    lo, hi = min(vals), max(vals); pad = (hi - lo) * 0.12 or 1
    for i, (x, y) in enumerate(zip(xs, ys)):
        last = i == len(xs) - 1
        ax.text(x, y + (-pad * 1.3 if last else pad * 0.45), fmt.format(y), ha="center", fontsize=6.6, color=acc if last else INK)
    if c.get("ref"):
        ax.axhline(c["ref"]["value"], color=acc, lw=0.8, ls=(0, (3, 2)))
        ax.text(xs[0], c["ref"]["value"] - pad * 0.3, c["ref"]["label"], fontsize=6.4, color=acc, va="top")
    ax.xaxis.set_major_formatter(md.DateFormatter("%d %b")); ax.tick_params(axis="x", labelsize=6.2)
    ax.set_yticks([]); ax.set_ylim(lo - pad * 2, hi + pad * 1.5)
    for s in ["top", "right", "left"]:
        ax.spines[s].set_visible(False)
    save(fig, out)


def rank(c, out):
    acc = c.get("accent", RED); fmt = c.get("fmt", "{:.2f}"); rows = c["items"]
    fig, ax = plt.subplots(figsize=(3.3, 0.3 * len(rows) + 0.2))
    ax.barh([r[0] for r in rows], [r[1] for r in rows], height=0.6, color=[acc if r[0] == c.get("highlight") else INK for r in rows])
    top = max(r[1] for r in rows) * 1.15
    for i, r in enumerate(rows):
        ax.text(r[1] + top * 0.01, i, fmt.format(r[1]), va="center", fontsize=6.8)
    if c.get("ref"):
        ax.axvline(c["ref"]["value"], color=acc, lw=0.7, ls=(0, (3, 2)))
        ax.text(c["ref"]["value"], -0.75, c["ref"]["label"], fontsize=6, color=acc, ha="center")
    ax.invert_yaxis(); ax.set_xlim(0, top); ax.set_xticks([]); off(ax); ax.tick_params(left=False, labelsize=7)
    save(fig, out)


def mapc(c, out):
    gj = json.load(open(os.path.join(KIT, "geo", "countries.geojson")))
    w, h = c.get("size", [4.6, 3.6])
    fig, ax = plt.subplots(figsize=(w, h))
    ax.set_facecolor("#e8eef0")
    hi = c.get("highlight", {})
    for f in gj["features"]:
        g = f["geometry"]; name = f["properties"].get("name", "")
        polys = g["coordinates"] if g["type"] == "MultiPolygon" else [g["coordinates"]]
        for p in polys:
            ax.add_patch(Polygon(p[0], closed=True, fc=hi.get(name, "#f2efe8"), ec="#8c8577", lw=0.4))
    x0, x1, y0, y1 = c["bbox"]
    ax.set_xlim(x0, x1); ax.set_ylim(y0, y1); ax.set_aspect(c.get("aspect", 1.1))
    ax.set_xticks([]); ax.set_yticks([]); off(ax)
    if c.get("arrow"):
        a = c["arrow"]
        ax.add_patch(FancyArrowPatch(tuple(a["from"]), tuple(a["to"]), connectionstyle=f"arc3,rad={a.get('rad', -0.25)}",
                                     arrowstyle="-|>", mutation_scale=12, lw=1.6, color=RED, linestyle=(0, (4, 2))))
        if a.get("label"):
            ax.text(a["at"][0], a["at"][1], a["label"], fontsize=6.6, color=RED, style="italic", ha="center", path_effects=HALO)
    for t, x, y in c.get("labels", []):
        ax.text(x, y, t, fontsize=7, color="#5b5548", ha="center", fontweight="bold", alpha=0.85)
    for t, x, y, rot in c.get("water", []):
        ax.text(x, y, t, fontsize=6.5, style="italic", color="#4c6670", rotation=rot, ha="center")
    for p in c.get("points", []):
        ax.plot(p["lon"], p["lat"], "o", ms=5, color=INK if p.get("black") else RED, mec="white", mew=0.8, zorder=5)
        if p.get("label"):
            ax.text(p["lon"] + p.get("dx", 0.5), p["lat"] + p.get("dy", 0), p["label"], fontsize=p.get("size", 6.8),
                    ha=p.get("ha", "left"), va="center", color=INK, linespacing=1.15,
                    fontweight="bold" if p.get("bold") else "normal", path_effects=HALO)
    save(fig, out)


def track(c, out):
    url = f"https://raw.githubusercontent.com/bacinger/f1-circuits/master/circuits/{c['circuit']}.geojson"
    gj = json.load(urllib.request.urlopen(url, timeout=30))
    coords = gj["features"][0]["geometry"]["coordinates"]
    lat0 = coords[0][1]
    xs = [p[0] * math.cos(math.radians(lat0)) for p in coords]; ys = [p[1] for p in coords]
    fig, ax = plt.subplots(figsize=(3.3, 2.0))
    ax.plot(xs, ys, color=INK, lw=4.2, solid_capstyle="round", solid_joinstyle="round")
    ax.plot(xs, ys, color="white", lw=1.0, solid_joinstyle="round")
    ax.plot(xs[0], ys[0], "s", color=RED, ms=6)
    ax.annotate(c.get("start_label", "Start / finish"), (xs[0], ys[0]), xytext=tuple(c.get("label_offset", [-60, -22])),
                textcoords="offset points", fontsize=6.6, color=RED, arrowprops=dict(arrowstyle="-", color=RED, lw=0.6))
    ax.set_aspect("equal"); ax.axis("off")
    save(fig, out)


KINDS = {"bars": bars, "targets": targets, "line": line, "rank": rank, "map": mapc, "track": track}

if __name__ == "__main__":
    folder = sys.argv[1]
    specs = json.load(open(os.path.join(folder, "charts.json")))
    for s in specs:
        out = os.path.join(folder, s["file"])
        try:
            KINDS[s["type"]](s, out)
            print("ok", s["file"])
        except Exception as e:
            print("FAILED", s["file"], e)
