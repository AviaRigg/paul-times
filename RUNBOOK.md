# The Paul Times: production runbook

This repo produces Paul's personal newspaper as an encrypted, swipeable iPhone web app,
served by GitHub Pages from `docs/`. A scheduled Claude session follows this file every
morning. Everything it needs is in this repo; it has no memory of earlier sessions.

Reader: Paul Chedozeau, rigging student and 3D artist (Maya 2026), delivery driver, lives in
Amsterdam, from Annecy, plans to move to Australia in May 2027.

## Editions

| Edition | When | Id | Covers | Size | Sudoku |
|---|---|---|---|---|---|
| Daily | Mon to Sat, 07:00 Amsterdam | `YYYY-MM-DD` | last 24 hours | 10 section pages (scroll inside each) | 2: `Medium:32,Hard:25` |
| Weekly | Sunday, 09:00 Amsterdam (replaces the Sunday daily) | `YYYY-MM-DD-weekly` | last 7 days | 10 section pages, about twice as long | 4: `Easy:38,Medium:32,Hard:26,Hard:24` |

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
4. Weather (Local section): you have no weather tool, so use WebSearch, for example
   "yr.no Amsterdam forecast" and "yr.no Annecy forecast", then WebFetch the yr.no forecast
   page from the results (fall back to another forecast site from the results if it fails).
   Get today's high, and min/max °C plus rain chance for the next 3 days, for both cities.
   NEVER copy the weather from a previous issue. If no forecast can be read, replace the
   weather box contents with "Weather unavailable today" and say so in your final report.
5. Create `issues/<id>/` and write:
   - `sections.html` (structure below). Copy the previous issue's file as the starting pattern.
   - `charts.json` (see `kit/charts.py` docstring for every chart type).
6. Build: `TPT_PASSWORD=<code from your task instructions> python kit/build.py <id> --edition daily --title "<short lead headline>" --sudoku Medium:32,Hard:25`
   Check the output: every chart "ok", no "WARNING". Fix and rebuild if not.
7. Optional self-check: open `build/<id>.html` in Playwright at 390x760 and confirm
   `document.querySelectorAll('.page').length` is 10 and nothing overflows horizontally.
8. Commit and push to `main`:
   `git add docs issues && git commit -m "Issue <id>" && git push`
   Never commit `build/` or the password. Never print the password in commit messages.
9. Wait about 90 seconds, then confirm `<site URL from README.md>/issues.json`
   lists the new id. Report the headline and anything that failed in one short message.

## Sections (in this order)

Each section is a `<section data-key data-title data-accent>` in `sections.html`. The big number in each section opener is its position (World 2, France 3, Local 4 ... Back Page 11).

1. **front** (`--a-front`): masthead (date, edition, issue number = previous + 1), two teasers
   (`data-goto` a section key), lead headline + dek, a big lead visual, In brief, 2 paragraphs,
   a "Continued in <section>" jump, "The day in five lines", **Number of the day**, contents
   (`#toc`, filled automatically).
   **The front lead is the single most important or exciting story for Paul today, from ANY
   section**, not automatically world news. Examples: "GTA 6 is out today", "Hamilton on pole
   in Austin", "Antonelli is world champion", a big French political crisis, a market crash
   that hits his ETFs, a major Maya or rigging release, or a war when it truly dominates.
   The front kicker names the section (for example "Breaking · Formula 1"), the "Continued in"
   jump points to that section, and the lead visual matches the story: a track map for F1,
   a chart for markets, a locator map for world events, a timeline or bar chart for games or
   tech. Real press photos are not available (no network access to photo sites, and they are
   copyrighted); draw the visual from real data with `kit/charts.py`.
2. **world** (`--a-world`): the main world story (continued from the front if it led), pull
   quote, locator map of the day's stories, 6 to 8 briefs. Global major events first, then minor
   ones.
3. **france** (`--a-france`): FRENCH POLITICS, VERY IMPORTANT TO PAUL, never skip it, at least
   one full article plus briefs. Government and Prime Minister, the Assemblée nationale and Senate
   (budget, votes, motions of censure), President Macron, parties and their leaders, protests and
   strikes, court cases involving politicians, and the 2027 presidential race (include the latest
   first-round poll as a `rank` chart, naming pollster, date and sample size, and saying it is a
   snapshot). Strictly neutral: report what each side says, no opinions. French sources first
   (franceinfo, Le Monde, Public Sénat, LCP, Les Echos), cross-checked.
   Always end the France section with a **"Lisnard watch"** box (David Lisnard, mayor of Cannes,
   Nouvelle Énergie, is Paul's preferred 2027 candidate): his latest polls (pollster, date, score,
   change), what he said or did, campaign news, social media momentum, plus a one-line "Reality
   check" on where he stands against the leaders. Factual, never promotional: include notable
   criticism of him when there is any. If nothing new happened, say so in one line and repeat the
   latest poll. Use `<figure class="photo portrait" data-wiki="fr|David_Lisnard" data-alt="David Lisnard"></figure>`
   at the top of the box.
4. **local** (`--a-local`): Annecy and Haute-Savoie lead with an illustration or chart, weather box
   for Amsterdam and Annecy (°C, today plus 3 days, rain %), a "Scooter check" line (he rides a
   scooter in Amsterdam), 3 to 4 Annecy briefs, **Dutch word of the day** (word, pronunciation,
   example sentence, bonus phrase; useful for a delivery driver).
5. **markets** (`--a-markets`): lead on the main market story, index-moves bar chart, "Other
   markets" table (AEX, CAC 40, EUR/USD, gold, Brent, US 10-year), then "Your portfolio":
   ETF weight-vs-target chart, Revolut table, eToro table, Straight talk.
6. **crypto** (`--a-crypto`): bitcoin lead with a dated line chart, price table (BTC, ETH, SOL,
   XRP, USDT, USDC), briefs on stablecoins, CBDCs (digital euro etc.), US and EU regulation,
   governments and bitcoin. Sudoku No. 1 (`<div class="sdk blk" data-sudoku="0"></div>`).
7. **tech** (`--a-tech`): AI lead, one chart, pull quote, tech and AI briefs, **Quote of the day**
   (real, correctly attributed, ideally public domain; tie it to rigging or craft in one line).
8. **craft** (`--a-craft`): 3D animation, rigging (top priority), 3D software (Maya, Blender,
   Houdini, ZBrush, Unreal), video games. **Tool of the week** (inverted box), **Rigging job board**
   (real openings with studio and location; say so if there are none), **Australia corner**
   (visas, VFX and animation hiring in Australia).
9. **sport** (`--a-sport`): F1 (results, standings, technical news; add a "Tech desk · for the SF-26
   project" box, he is rigging an F1 car), tennis (big results and French players), Les Bleus
   (men's national team; results strip), **On this day** (3 dated historical events for today).
10. **week** (`--a-week`): timeline list of the next 10 days including key French political dates (`ol.tl`, mark the biggest item `hot`),
   editorial (one opinion piece on the top story, ending with the opposing view), Sudoku No. 2
   (`data-sudoku="1"`). Weekly: put Sudoku 3 and 4 here too.
11. **back** (`--a-back`): **Rigging tip of the day** (Maya 2026, practical, with a short
    `maya.cmds` snippet that actually works), sources by section, "Past issues" link, footer note.

## Writing rules

- English. Never use em dashes or en dashes. Metric units only. Times in Amsterdam time.
- Paraphrase everything. At most one short quote (under 15 words) per source. No song lyrics.
- Big stories: In brief box, then the full story. Small stories: a brief (kicker, h4, 1 to 3 sentences).
- Blunt and specific. Make the "why it matters to you" link when it is real (portfolio, scooter,
  SF-26, AviaRigg, Australia), never forced.
- Political topics: neutral, factual, no opinions except in the labelled editorial, which must
  present the other side.

## Photos

Real photos come from Wikimedia Commons and are loaded by Paul's phone when he opens the issue,
with the photographer and licence credit added automatically. Only free-licence Commons files are
shown; anything else is skipped silently. Never use photos from Google, news sites or agencies.

- `<figure class="photo blk" data-wiki="en|Article_Title" data-alt="..."><figcaption><b>Title.</b> Text.</figcaption></figure>`
  uses the lead image of a Wikipedia article (people, places, circuits, companies, games' developers).
  Prefer `fr|...` for French people and places.
- `data-commons="search words"` searches Commons and takes the first hit. Last resort only: hits can be unrelated old events (a search for a tanker near Hormuz returned a 2012 US Navy collision). Prefer `data-wiki` (the Wikipedia article's lead image) or an exact `data-file`. Never use a photo of a different event as if it showed today's news; caption file images as file images.
- `data-file="File:Exact_name.jpg"` for a specific Commons file.
- Add `portrait` to the class for a small portrait floated beside text.
Use 3 to 6 photos per issue: one on the front lead when a relevant photo exists (a file photo is
fine, say "File photo" in the caption), plus people in the news (politicians, drivers, players).
Photos complement the data charts; they never replace a chart that carries numbers.

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
