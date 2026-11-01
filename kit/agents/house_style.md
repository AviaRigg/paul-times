# House style: the layout of issue No. 1 (15 Oct 2026)

Paul compared issue No. 1 with No. 18 on 1 Nov 2026 and found the layout had drifted: section openers gone,
masthead scrambled, teasers without their line of text, sudokus dropped into the middle of lead stories, week
dates crammed into a 68 px column, the back page a pile of grey boxes, raw URLs overflowing the screen, almost
no pull quotes. The cause: each run copied the previous issue's skeleton, so every small slip was inherited.
**This file is the reference, not yesterday's issue.** `kit/lint.py` blocks the structural slips listed here.

## Front page (editor), in this order

```html
<div class="mast blk"><div class="meta"><span>{{EDITION}} · No. {{NO}}</span><span>Amsterdam · Annecy</span><span>Sun 1 Nov 2026</span></div>
  <div class="name">The Paul Times</div><div class="motto">Your daily paper, from the first coffee to the last parcel</div>
  <div class="rail">FORMULA 1 · FRANCE · WORLD · MARKETS · CRYPTO · TECH · CRAFT</div></div>
<div class="teasers blk">
  <button class="teaser" data-goto="france"><span class="pg">France</span><span class="t">Short headline, 3 to 6 words</span>One line of detail, about 12 to 18 words.</button>
  <button class="teaser" data-goto="world"><span class="pg">World</span><span class="t">Short headline</span>One line of detail.</button></div>
<div class="lead blk kn" data-more="lead"><div class="kicker">Breaking · Formula 1</div><h1>Lead headline</h1><p class="dek">Dek</p></div>
<figure class="photo blk" data-src=... data-credit=... data-link=...>...</figure>
<div class="inbrief blk">...</div> <p class="blk drop">...</p> <p class="blk">...</p>
<div class="jump blk" data-goto="sport">Continued in Sport →</div>
<div class="five blk"><div class="kicker">The day in five lines</div><p><b>1</b>One short line.</p> ... five lines</div>
<div class="fun blk"><span class="lbl">Number of the day</span><span class="big">0.009 s</span><p>One sentence.</p></div>
<div class="blk"><div class="kicker">Inside · tap to jump</div><div class="toc" id="toc"></div></div>
```

- `.meta` is three spans (edition and number, places, short date); `.rail` lists the day's sections in capitals, ordered by the day's news.
- Teasers always carry the line of text after `.t`. Headlines in `.t` stay short.
- The five lines are one short line each (under 12 words), no "Topic:" prefixes.

## Every other section

- **Opener**: added by `kit/assemble.py` (big section name, "Section N", italic tagline). Never write one by hand, never remove it.
- **The section that continues the front lead** uses the kicker `Continued from the front` on its lead `.head`.
- **Lead story order**: `.head`, big photo (`data-src`), `.inbrief`, `p.drop`, `p`, optional `.pull`, more `p`, then boxes and briefs.
- **Pull quotes**: at least two in the paper (`<div class="pull blk"><span class="q">“</span><p>Quote under 15 words.</p><div class="who">Who, where</div></div>`).
- **Photos**: 20 to 30 per issue, a second photo inside long stories, `portrait` figures for people in briefs.
- **Sudokus**: placed by `kit/assemble.py` between stories, never inside a lead story.

## The Week Ahead (editor)

```html
<ol class="tl blk">
  <li class="hot"><span class="d"><em>Sun 1</em></span>Mexico City Grand Prix, 20:00, Antonelli can be champion</li>
  <li><span class="d">Mon 2</span>Short item · second item</li>
  <li><span class="d">12 Nov</span>Item beyond the week</li>
</ol>
<div class="head blk kn"><div class="kicker">Editorial</div><h3>Opinion headline</h3></div>
<p class="blk drop">...</p><p class="blk">...</p>
<p class="blk note">Opinion. The other side: ...</p>
```

- The date label is at most 9 characters (`Sun 1`, `Tue 10`, `12 Nov`); times go in the text. Keep items short, joined with ` · `.
- No extra headline above the timeline: the opener is the title.

## Back page (editor)

```html
<!--CHECKED-->
<div class="box blk"><h4>Corrections</h4><p>...</p></div>
<!--TIP-->
<div class="sources blk"><div class="kicker">Sources</div>
  <p><b>World:</b> <a href="URL">Outlet: title</a>, <a href="URL">Outlet: title</a>.</p>
  ... one <p> per section ...</div>
<div class="feedback blk" data-feedback></div>
<p class="blk"><a href="./?archive">Past issues →</a></p>
<p class="blk note">The Paul Times is compiled by Claude from public reporting. Figures are as published at press time; check before acting on them.</p>
```

- `checked.json` notes name the outlet only, never a raw URL (URLs overflow the phone screen).
