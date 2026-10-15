# The Paul Times: production runbook

This repo produces Paul's personal newspaper as an encrypted, swipeable iPhone web app,
served by GitHub Pages from `docs/`. A scheduled Claude session follows this file every
morning. Everything it needs is in this repo; it has no memory of earlier sessions.

Reader: Paul Chedozeau, rigging student and 3D artist (Maya 2026), delivery driver, lives in
Amsterdam, from Annecy, plans to move to Australia in May 2027.

## Editions

| Edition | When | Id | Covers | Size | Sudoku |
|---|---|---|---|---|---|
| Daily | Mon to Sat, 07:00 Amsterdam | `YYYY-MM-DD` | last 24 hours | about 40 to 45 phone screens | 2: `Medium:32,Hard:25` |
| Weekly | Sunday, 09:00 Amsterdam (replaces the Sunday daily) | `YYYY-MM-DD-weekly` | last 7 days | about 70 to 90 screens | 4: `Easy:38,Medium:32,Hard:26,Hard:24` |

## Steps

1. `pip install --break-system-packages -q matplotlib cryptography pillow` if missing.
2. Research every section (below) with web search. Search for each section separately; prefer
   original sources. Verify numbers against a second source when they disagree; if they still
   disagree, say so in the copy ("snapshot, treat as approximate"). Never invent a figure.
3. Portfolio data (Markets section, "Your portfolio"):
   - eToro: `get-my-portfolio-summary` (read only, never trade). Total value, open P&L, copied
     traders with value, open P&L and share, direct holdings.
   - Revolut ETFs: Google Sheet `ETF_Investment_Plan`
     (id `16xAAN9Urk_NPYZezI_LdFnqFYpn7DZ8c5v3wSRznOHE`), range `Holdings!B7:O20`:
     ETF, value €, unrealised %, weight, target.
   - If a connector is unavailable, keep yesterday's structure and print "Not updated today:
     <source> unavailable" in the box. Never guess holdings.
   - Write one blunt "Straight talk" line: biggest gap between weight and target, and what his
     next weekly buys should favour. He rebalances only by adding money (no selling).
     End with "Information, not financial advice."
4. Create `issues/<id>/` and write:
   - `sections.html` (structure below). Copy the previous issue's file as the starting pattern.
   - `charts.json` (see `kit/charts.py` docstring for every chart type).
5. Build: `TPT_PASSWORD=<code from your task instructions> python kit/build.py <id> --edition daily --title "<short lead headline>" --sudoku Medium:32,Hard:25`
   Check the output: every chart "ok", no "WARNING". Fix and rebuild if not.
6. Optional self-check: open `build/<id>.html` in Playwright at 390x760 and confirm
   `document.querySelectorAll('.page').length` is in range and no page body has class `overflow`.
7. Commit and push to `main`:
   `git add docs issues && git commit -m "Issue <id>" && git push`
   Never commit `build/` or the password. Never print the password in commit messages.
8. Wait about 90 seconds, then confirm `<site URL from README.md>/issues.json`
   lists the new id. Report the headline and the screen count in one short message.

## Sections (in this order)

Each section is a `<section data-key data-title data-accent>` in `sections.html`.

1. **front** (`--a-front`): masthead (date, edition, issue number = previous + 1), two teasers
   (`data-goto` a section key), lead headline + dek, lead map or chart, In brief, 2 paragraphs,
   "Continued in The World", "The day in five lines", **Number of the day**, contents (`#toc`,
   filled automatically), reading-mode switch.
2. **world** (`--a-world`): lead continued (3 paragraphs), pull quote, locator map of the day's
   stories, 6 to 8 briefs. Global major events first, then minor ones.
3. **local** (`--a-local`): Annecy and Haute-Savoie lead with an illustration or chart, weather box
   for Amsterdam and Annecy (°C, today plus 3 days, rain %), a "Scooter check" line (he rides a
   scooter in Amsterdam), 3 to 4 Annecy briefs, **Dutch word of the day** (word, pronunciation,
   example sentence, bonus phrase; useful for a delivery driver).
4. **markets** (`--a-markets`): lead on the main market story, index-moves bar chart, "Other
   markets" table (AEX, CAC 40, EUR/USD, gold, Brent, US 10-year), then "Your portfolio":
   ETF weight-vs-target chart, Revolut table, eToro table, Straight talk.
5. **crypto** (`--a-crypto`): bitcoin lead with a dated line chart, price table (BTC, ETH, SOL,
   XRP, USDT, USDC), briefs on stablecoins, CBDCs (digital euro etc.), US and EU regulation,
   governments and bitcoin. Sudoku No. 1 (`<div class="sdk blk" data-sudoku="0"></div>`).
6. **tech** (`--a-tech`): AI lead, one chart, pull quote, tech and AI briefs, **Quote of the day**
   (real, correctly attributed, ideally public domain; tie it to rigging or craft in one line).
7. **craft** (`--a-craft`): 3D animation, rigging (top priority), 3D software (Maya, Blender,
   Houdini, ZBrush, Unreal), video games. **Tool of the week** (inverted box), **Rigging job board**
   (real openings with studio and location; say so if there are none), **Australia corner**
   (visas, VFX and animation hiring in Australia).
8. **sport** (`--a-sport`): F1 (results, standings, technical news; add a "Tech desk · for the SF-26
   project" box, he is rigging an F1 car), tennis (big results and French players), Les Bleus
   (men's national team; results strip), **On this day** (3 dated historical events for today).
9. **week** (`--a-week`): timeline list of the next 10 days (`ol.tl`, mark the biggest item `hot`),
   editorial (one opinion piece on the top story, ending with the opposing view), Sudoku No. 2
   (`data-sudoku="1"`). Weekly: put Sudoku 3 and 4 here too.
10. **back** (`--a-back`): **Rigging tip of the day** (Maya 2026, practical, with a short
    `maya.cmds` snippet that actually works), sources by section, "Past issues" link, footer note.

## Writing rules

- English. Never use em dashes or en dashes. Metric units only. Times in Amsterdam time.
- Paraphrase everything. At most one short quote (under 15 words) per source. No song lyrics.
- Big stories: In brief box, then the full story. Small stories: a brief (kicker, h4, 1 to 3 sentences).
- Blunt and specific. Make the "why it matters to you" link when it is real (portfolio, scooter,
  SF-26, AviaRigg, Australia), never forced.
- Political topics: neutral, factual, no opinions except in the labelled editorial, which must
  present the other side.

## sections.html building blocks

Every top-level child of a section needs class `blk` (one swipeable unit; the paginator never
splits a block). Add `kn` to headings so they stay with the next block. Available pieces:

- `<div class="head blk kn"><div class="kicker">Lead · Topic</div><h3>Headline</h3></div>`
- `<div class="inbrief blk"><b class="l">In brief</b>...</div>`
- `<p class="blk drop">First paragraph with drop cap</p>`, `<p class="blk">...</p>`
- `<figure class="blk"><div class="plate"><img src="file.png" alt="..."></div><figcaption><b>Title.</b> Text. <span class="cr">Data: ...</span></figcaption></figure>`
  (`src` is a bare filename in the issue folder; the build inlines it)
- `<div class="brief blk"><div class="kicker">Place</div><h4>Headline</h4><p>Text</p></div>`
- `<div class="pull blk"><span class="q">“</span><p>Quote</p><div class="who">Who</div></div>`
- `<div class="box blk"><h4>Title</h4><div class="tbl"><table>...</table></div></div>`
  (`box inv` for an inverted box; table cells `class="r"` right-align, `up`/`down` colour changes)
- `<div class="fun blk"><span class="lbl">Label</span>...</div>` with `.big`, `.word`, `.pron`, `.yr`, `.q`
- `<div class="strip blk">` results strip, `<ol class="tl blk">` timeline, `.wx` weather grid
- Keep blocks under about 550 px tall at 390 px wide; split long stories into several `<p class="blk">`.
