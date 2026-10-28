# Shared rules for every research agent (read this once, then your own brief)

You are one of up to 4 research agents building ONE part of today's Paul Times. Your job is depth and accuracy:
research properly, then write your section as FINAL HTML fragments straight into the file(s) named in your brief
under `issues/<id>/parts/`. Do not write notes first and re-write them later: the fragment IS the deliverable
(write the file as you go, so a cut-off still leaves usable work). Hard caps: 25 web searches and 12 WebFetch
page reads in total (full pages are the biggest cost; prefer facts from search results and read a page only when
you need its details, photo or caption; image checks with curl do not count). When either cap is reached, stop researching and finish writing. Do not put the section's `<section>` wrapper, sudokus, the section number
or any inline style in the fragment: `kit/assemble.py` adds the wrapper and places the sudokus. You may use the
placeholders `{{NO}}`, `{{DATE}}`, `{{WEEKDAY}}`, `{{EDITION}}`. When done, reply with at most 6 lines: files written,
counts (briefs, photos, `more` templates), sources you could not read, anything unverified. Do not paste the content back.

## Research rules

Research your sections with web search. Search for each section separately; prefer original sources. Verify numbers against a second source when they disagree; if they still disagree, say so in the copy ("snapshot, treat as approximate"). Never invent a figure.

No `charts.json`, no drawn visuals. Paul's rule: never draw graphs, charts, maps or schematics. Visuals are real photos only (see Photos). Numbers go in tables, strips and text.

## Fetching in unattended runs

Nobody can tap "Allow" during a scheduled run, so every web read must work without approval. The
scheduled tasks already run with automatic approval, but the WebFetch tool still asks a human for any
address it did not receive from a search result or a page it read: hand-built URLs (an oEmbed link,
a "/m/title" Rotten Tomatoes path, a site's home page, a date page like ".../2026/10/20/") stall
until the request times out and the agent loses the item. Rules, for you and for every research agent
(copy them into each agent's prompt):
1. **Search first, then fetch.** Only WebFetch a URL that appeared verbatim in a WebSearch result or
   in a page you already fetched in the same agent. Never type, guess or edit a URL. If the page you
   need did not come up, search again with the outlet's name in the query.
2. **Do not spend searches on blocked sites.** These cannot be read at all (blocked or robots.txt,
   tested 20 to 21 Oct 2026): ledauphine.com, lemessager.fr, franceinfo.fr, france3-regions,
   ici.fr (France Bleu), cnews.fr, coindesk.com articles, cointelegraph, stockanalysis.com,
   rottentomatoes.com scores, youtube.com pages. Use them only as headlines when a search result
   names them, and cite the article you actually read.
   - French politics instead of franceinfo: Public Sénat, LCP, Le Monde, Les Echos, 20 Minutes,
     Ouest-France, Le Figaro, Le Parisien, BFMTV, Brut (via search).
   - Annecy and Haute-Savoie instead of Le Dauphiné and Le Messager: ODS Radio (odsradio.com, which
     has photos), faitsdivers365.fr (aggregator of Dauphiné and Messager headlines), actu.fr,
     8 Mont-Blanc, Radio Mont-Blanc, annecy.fr and grand-annecy.fr, Haute-Savoie prefecture. Search
     "odsradio Annecy <topic>" or "<town> <topic> octobre 2026". The local lead photo comes from the
     first of these that has one; only if none does, use a `data-wiki` place photo marked "File photo".
3. **curl** is for checking a URL you already have (image status codes, job links), never for reading
   a page that WebFetch could not read.
4. In the final report, list what could not be read and which fallback you used.

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

Volume: daily 12 to 20 images, Sunday 25 or more. Front lead always has one. Every section
lead has one. Never use a photo of a different event as if it showed today's news; say
"File photo" in the caption when the image is not of the event itself.

## Building blocks

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

### Tap for more (every story)

Paul can tap any story and a full-screen sheet opens with the deeper version (`docs/screen-overlay.js`,
nothing to build). Give EVERY `.brief` and EVERY big story's `.head` a deeper version, written as the
LAST child of that block:
`<template class="more"> ... </template>`
Tapping the brief, the headline, or any paragraph, In brief or pull quote of that big story opens it.
A "More ›" marker appears on the headline automatically.

- **Brief**: EVERY brief in every section gets one, no exceptions (Paul's request, 17 Oct 2026:
  small stories with no deeper text are a gap). 1 to 2 solid paragraphs are enough: what happened
  in more detail (numbers, names, where and when), the background needed to understand it, and
  what happens next with dates, plus sources. Never just repeat the printed brief. Ask each research
  agent for 2 to 3 extra facts per brief so this needs no extra searching. Before building, count:
  every `.brief` must contain a `<template class="more">`.
- **Big story** (`.head`): 4 to 8 paragraphs that go BEYOND the printed article (do not repeat it):
  `<h5>Background</h5>`, `<h5>Key facts</h5>` as a `<ul>`, `<h5>What happens next</h5>`, a
  timeline `<ol class="tl">` when the story has history, an extra photo different from the printed one,
  and a video when there is a real one (press conference, onboard lap, game or film trailer,
  launch footage, official channel only): `<div class="vid" data-yt="<id>"><span>Caption</span></div>`,
  id taken from an article embed as in the Screen section; never invent one.
- **Feature boxes** (Stock of the day, Radar, Tool of the week, Lisnard watch, Tech desk, Australia
  corner, Rigging job board) also get one: more numbers, the full case for and against, links.
  Tables and scoreboards with nothing more to say get none.
- `<div class="you">...</div>` for "Why it matters to you" when the link is real (portfolio,
  scooter, SF-26, AviaRigg, Australia), never forced.
- Always end with `<div class="srcs"><a href="URL">Outlet: article title</a> ...</div>` (2 to 4 real
  URLs you actually read). Same writing rules as the paper: paraphrase, no em or en dashes, metric.
- Front lead: do not duplicate. Give the section's lead template `data-id="lead"` and the front
  `.head` the attribute `data-more="lead"`.
- Allowed inside: `p`, `h5`, `ul`, `ol.tl`, `.tbl` table, `figure.photo` (`data-src` with
  `data-credit`/`data-link`, or `data-wiki`), `.vid`, `.you`, `.pull`, `.srcs`.
- Time: write it from the research you already did for the story. The only extra searching is for a
  video id. If the run is running late, cover the big stories and feature boxes first, then the
  briefs, but every brief must have its template before the final push.

## Language

Paul picks the paper's language in the app's Settings; step 4b prints `LANGUAGE: en` or `fr`
(default English). For `fr`, write the entire issue in natural French as a French journalist
would (not a literal translation): headlines, body, captions, boxes, section `data-title`s
(Le Monde, France, Local, Marchés, Crypto, Tech et IA, Le Métier, Sport, Écrans, La Semaine,
Dernière page) and opener names, picks' "why" lines, claims. Keep "The Paul Times" as the
masthead. Same rules: no em or en dashes, metric, French number style (12,5 %, 5 000), dates
like "jeudi 15 octobre". The app's buttons switch language by themselves.
