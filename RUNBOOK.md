# The Paul Times: production runbook

This repo produces Paul's personal newspaper as an encrypted, swipeable iPhone web app,
served by GitHub Pages from `docs/`. A scheduled Claude session follows this file every
morning. Everything it needs is in this repo; it has no memory of earlier sessions.

Reader: Paul Chedozeau, rigging student and 3D artist (Maya 2026), delivery driver, lives in
Amsterdam, from Annecy, plans to move to Australia in May 2027.

## Editions

| Edition | When | Id | Covers | Size | Sudoku |
|---|---|---|---|---|---|
| Daily | Mon to Sat, starts 03:30, ready by 04:00 Amsterdam | `YYYY-MM-DD` (the morning's date) | YESTERDAY's news (previous calendar day) plus major overnight events; markets at yesterday's close | 10 section pages (scroll inside each) | 2: `Medium:32,Hard:25` |
| Weekly | Sunday, 09:00 Amsterdam (replaces the Sunday daily) | `YYYY-MM-DD-weekly` | last 7 days | 10 section pages, about twice as long | 4: `Easy:38,Medium:32,Hard:26,Hard:24` |

## Steps

1. `pip install --break-system-packages -q cryptography pillow` if missing.
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
4. Weather (Local section): the weather box is LIVE. Paul's phone fetches Open-Meteo when he
   opens the issue and renders the Amsterdam rain-gear verdict (YES / pack it / no), hourly
   strip, wind for the scooter, what to wear, dark-from time, 3 days, and Annecy. The box must
   be `<div class="box wxl blk" data-wx><h4>Weather</h4> ...printed fallback... </div>`.
   The printed fallback is only shown if the live fetch fails: research it with WebSearch
   (for example "yr.no Amsterdam forecast", then WebFetch the page), give today's Amsterdam
   rain verdict in one line ("Rain gear: yes, showers 14:00 to 18:00"), today plus 3 days for
   both cities. NEVER copy weather from a previous issue; if nothing can be read, the fallback
   is just "Live forecast loads when you open the issue." Do not write a separate
   "Scooter check" paragraph; the live box covers it.
5. Create `issues/<id>/` and write:
   - `sections.html` (structure below). First unlock the previous issue's source with
     `TPT_PASSWORD=<code> python kit/unlock.py <previous id>`, then copy it as the starting pattern,
     but follow THIS file where they differ (older issues contain charts; new ones must not).
   - NO `charts.json`. Paul's rule: never draw graphs, charts, maps or schematics. Visuals are
     real photos only (see Photos). Numbers go in tables, strips and text.
6. Build: `TPT_PASSWORD=<code from your task instructions> python kit/build.py <id> --edition daily --title "<short lead headline>" --sudoku Medium:32,Hard:25`
   Check the output: no "WARNING". Fix and rebuild if not.
7. Optional self-check: open `build/<id>.html` in Playwright at 390x760 and confirm
   `document.querySelectorAll('.page').length` is 12 and nothing overflows horizontally.
8. Commit and push to `main`:
   `git add docs issues && git commit -m "Issue <id>" && git push`
   Plain `issues/*/sections.html` is gitignored on purpose: the repo is public and it holds Paul's
   portfolio. The build writes an encrypted `sections.enc` next to it, and that is what gets
   committed. Never force-add the plain file.
   Never commit `build/` or the password. Never print the password in commit messages.
9. Wait about 90 seconds, then confirm `<site URL from README.md>/issues.json`
   lists the new id. Report the headline and anything that failed in one short message.

## Sections (in this order)

Each section is a `<section data-key data-title data-accent>` in `sections.html`. The big number in each section opener is its position (World 2, France 3, Local 4 ... Sport 9, Screen 10, Week 11, Back Page 12).

1. **front** (`--a-front`): masthead (date, edition, issue number = previous + 1), two teasers
   (`data-goto` a section key), lead headline + dek, a big lead PHOTO, In brief, 2 paragraphs,
   a "Continued in <section>" jump, "The day in five lines", **Number of the day**, contents
   (`#toc`, filled automatically).
   **The front lead is the single most important or exciting story for Paul today, from ANY
   section**, not automatically world news. Examples: "GTA 6 is out today", "Hamilton on pole
   in Austin", "Antonelli is world champion", a big French political crisis, a market crash
   that hits his ETFs, a major Maya or rigging release, or a war when it truly dominates.
   The front kicker names the section (for example "Breaking · Formula 1"), the "Continued in"
   jump points to that section, and the lead photo matches the story: the driver or circuit
   for F1, the game's studio or franchise for games, the place for world events, the
   politician for politics, the company or its headquarters for markets and tech.
2. **world** (`--a-world`): the main world story (continued from the front if it led), pull
   quote, a photo (place or person in the story), 6 to 8 briefs. Global major events first, then minor
   ones.
3. **france** (`--a-france`): FRENCH POLITICS, VERY IMPORTANT TO PAUL, never skip it, at least
   one full article plus briefs. Government and Prime Minister, the Assemblée nationale and Senate
   (budget, votes, motions of censure), President Macron, parties and their leaders, protests and
   strikes, court cases involving politicians, and the 2027 presidential race (include the latest
   first-round poll as a table, naming pollster, date and sample size, and saying it is a
   snapshot). Photos of the politicians in the news (`fr|` Wikipedia articles). Strictly neutral: report what each side says, no opinions. French sources first
   (franceinfo, Le Monde, Public Sénat, LCP, Les Echos), cross-checked.
   Always end the France section with a **"Lisnard watch"** box (David Lisnard, mayor of Cannes,
   Nouvelle Énergie, is Paul's preferred 2027 candidate): his latest polls (pollster, date, score,
   change), what he said or did, campaign news, social media momentum, plus a one-line "Reality
   check" on where he stands against the leaders. Factual, never promotional: include notable
   criticism of him when there is any. If nothing new happened, say so in one line and repeat the
   latest poll. Use `<figure class="photo portrait" data-wiki="fr|David_Lisnard" data-alt="David Lisnard"></figure>`
   at the top of the box.
4. **local** (`--a-local`): Annecy and Haute-Savoie lead with a photo of the place, the live weather box
   (step 4), 3 to 4 Annecy briefs, **Dutch word of the day** (word, pronunciation,
   example sentence, bonus phrase; useful for a delivery driver).
5. **markets** (`--a-markets`): lead on the main market story with a photo (company, exchange or
   person), index-moves table (green up, red down), "Other markets" table (AEX, CAC 40, EUR/USD,
   gold, Brent, US 10-year), then "Your portfolio": Revolut table with weight and target
   columns, eToro table, Straight talk.
6. **crypto** (`--a-crypto`): bitcoin lead with a photo, price table (with 24 h and 7 d change) (BTC, ETH, SOL,
   XRP, USDT, USDC), briefs on stablecoins, CBDCs (digital euro etc.), US and EU regulation,
   governments and bitcoin. Sudoku No. 1 (`<div class="sdk blk" data-sudoku="0"></div>`).
7. **tech** (`--a-tech`): AI lead with a photo (company, product or person), pull quote, tech and AI briefs, **Quote of the day**
   (real, correctly attributed, ideally public domain; tie it to rigging or craft in one line).
8. **craft** (`--a-craft`): 3D animation, rigging (top priority), 3D software (Maya, Blender,
   Houdini, ZBrush, Unreal), video games. **Tool of the week** (inverted box), **Rigging job board**
   (real openings with studio and location; say so if there are none), **Australia corner**
   (visas, VFX and animation hiring in Australia). Photos: studios, software makers, games.
9. **sport** (`--a-sport`): F1 (results, standings, technical news; add a "Tech desk · for the SF-26
   project" box, he is rigging an F1 car; standings as a table), tennis (big results and French players), Les Bleus
   (men's national team; results strip), **On this day** (3 dated historical events for today).
10. **screen** (`--a-screen`, data-title "Screen"): films and TV, picked for Paul's taste.
   His taste: animation films (Pixar, DreamWorks, Disney, Sony Animation, Ghibli, French animation),
   Marvel, big blockbusters, French films. TV: Rick and Morty, Brooklyn Nine-Nine, Modern Family,
   Suits, Star Wars series (The Mandalorian, Andor, Ahsoka etc.); of Marvel series he has only
   watched Loki. Skip horror and prestige drama unless it is huge news.
   - **Lead**: the biggest film or TV story of the day in his lanes (a trailer, a release, box
     office, a casting, a renewal), with a photo (poster or still via the article's lead image).
   - **Rotten Tomatoes box**: table of recent releases in his lanes (last 4 to 6 weeks): title,
     Tomatometer %, Popcornmeter %, one-word verdict. Get scores from rottentomatoes.com (WebFetch
     the film page); if it cannot be read, use a news report that quotes the scores and say
     "via <source>". Never invent a score; write "n/a" if none found.
   - **Coming soon**: next releases in his lanes with Netherlands cinema date (Pathé/Vue
     Amsterdam, original version) and France date for French films; streaming premieres with
     platform (Netflix, Disney+, Prime Video, Max).
   - **Your shows**: any news on his shows (new season, episode, trailer, cast, renewal). If
     nothing, skip it rather than pad.
   - **Tonight's pick + My list** (always last): 5 picks he probably has not seen, best first,
     matched to his taste (comedy like B99 and Modern Family, adult animation like Rick and Morty,
     legal drama like Suits, Star Wars, Marvel, great animation films), with where to stream in the
     Netherlands and why in one line:
     `<div class="pick blk" data-pick='[{"t":"Title","y":"2021","kind":"Animated series","where":"Netflix","rt":"100%","why":"Why HE would like it","img":"optional image URL","link":"optional URL"}]'></div>`
     then `<div class="mylist blk" data-mylist></div>`. His phone shows one pick at a time with
     "Seen it / Not for me / + My list" buttons, remembers the taps and keeps his list. You cannot
     see those taps, so never repeat a title that was in a pick list in the last 30 issues
     (unlock and check the previous issues' sources). Only give an "rt" you verified. Weekly: 8 picks.
   Photos: posters, stills and trailer frames from studio pages or news articles (route 1 or 2 in
   Photos). Weekly edition: add the week's box office top 5 (worldwide) and all trailers released.
11. **week** (`--a-week`): timeline list of the next 10 days including key French political dates (`ol.tl`, mark the biggest item `hot`),
   editorial (one opinion piece on the top story, ending with the opposing view), Sudoku No. 2
   (`data-sudoku="1"`). Weekly: put Sudoku 3 and 4 here too.
12. **back** (`--a-back`): **Rigging tip of the day** (Maya 2026, practical, with a short
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

Paul wants LOTS of real images. Every major article and major event gets one, and so does any
small story that is visual (a protest, a crash, a launch, a new car, a game trailer, a tool UI).
If you write something that makes the reader want to see it, show it. Never draw charts, maps,
diagrams or illustrations instead. Images load on Paul's phone when he opens the issue; a figure
whose image fails stays hidden, so a wrong guess costs nothing but a correct one is gold.

Where to get each kind (in this order):
1. **News events (protests, disasters, launches, matches):** the lead photo of a news article
   about that exact event. WebFetch the article with the prompt "Give the exact absolute URL of
   the article's lead photo (og:image or first photo), its caption and photo credit, verbatim."
   Good sources: euronews, franceinfo, Le Monde, BBC, Reuters, AP, The Verge, cgchannel. Use it with
   `data-src`, `data-credit` (the photographer or agency exactly as credited) and `data-link`
   (the article URL). Skip images described as illustration, stock or AI-generated, and generic
   site logos or default images (for example `ps-default.png`). The caption must say where and
   when the photo was taken, from the source caption, never invented.
2. **Software, tools, plugins, games:** a real screenshot from the official release notes,
   product page or GitHub release (`https://github.com/user-attachments/assets/<uuid>` is
   stable; strip the signed `private-user-images` URL down to the uuid). For games, the
   official store or press page image.
3. **F1 circuits:** the official layout map from formula1.com. WebFetch
   `https://www.formula1.com/en/racing/<year>/<race-slug>` and ask for the track map URL (it
   looks like `.../common/f1/<year>/track/<year>track<name>detailed.webp`). Add class `light`.
   Drivers, cars and team bosses: the Wikipedia lead image (`data-wiki="en|Driver_Name"`) or a
   press photo of the actual weekend via route 1.
4. **People, places, companies (background, not a specific event):** `data-wiki="en|Article"`
   (`fr|` for French people and places). `data-file="File:..."` for an exact Commons file.
5. `data-commons="search words"` only as a last resort (hits are often unrelated old events).

Markup:
- `<figure class="photo blk" data-src="IMAGE_URL" data-credit="AP Photo/Name" data-link="ARTICLE_URL" data-alt="..."><figcaption><b>Place, date.</b> What it shows.</figcaption></figure>`
- `<figure class="photo blk" data-wiki="en|Article_Title" data-alt="..."><figcaption><b>Title.</b> Text.</figcaption></figure>`
- Add `portrait` for a small portrait floated beside text (people), `light` for maps or UI
  screenshots with transparent backgrounds.
The credit and an "open source" link are added automatically.

Check before publishing: for every `data-src` URL run
`curl -s -o /dev/null -m 15 -w '%{http_code}' "<url>"`. 200 means keep it. A 403, 404 or 410 from
the site itself means find another image. `000` (blocked by this session's network) means you
cannot check, so keep it. Report how many images you checked and how many you dropped.

Volume: daily 12 to 20 images, weekly 25 or more. Front lead always has one. Every section
lead has one. Never use a photo of a different event as if it showed today's news; say
"File photo" in the caption when the image is not of the event itself.

## sections.html building blocks

Every top-level child of a section needs class `blk` (one swipeable unit; the paginator never
splits a block). Add `kn` to headings so they stay with the next block. Available pieces:

- `<div class="head blk kn"><div class="kicker">Lead · Topic</div><h3>Headline</h3></div>`
- `<div class="inbrief blk"><b class="l">In brief</b>...</div>`
- `<p class="blk drop">First paragraph with drop cap</p>`, `<p class="blk">...</p>`
- `<div class="brief blk"><div class="kicker">Place</div><h4>Headline</h4><p>Text</p></div>`
- `<div class="pull blk"><span class="q">“</span><p>Quote</p><div class="who">Who</div></div>`
- `<div class="box blk"><h4>Title</h4><div class="tbl"><table>...</table></div></div>`
  (`box inv` for an inverted box; table cells `class="r"` right-align, `up`/`down` colour changes)
- `<div class="fun blk"><span class="lbl">Label</span>...</div>` with `.big`, `.word`, `.pron`, `.yr`, `.q`
- `<div class="strip blk">` results strip, `<ol class="tl blk">` timeline, `.wx` weather grid
- Keep blocks under about 550 px tall at 390 px wide; split long stories into several `<p class="blk">`.
