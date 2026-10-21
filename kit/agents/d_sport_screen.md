# Brief: Sport and Screen (including trailer ids and picks)

First read `kit/agents/_common.md`. You write: `parts/sport.html`, `parts/screen.html`, `parts/picks.json`

The editor read Paul's taps for you: `issues/<id>/taps.txt` (SEEN / MY LIST / NOT FOR ME) and the do-not-repeat digest `issues/<id>/history.txt`.

## Using Paul's taps (issues/<id>/taps.txt)

Every SEEN series (including ones he added himself) joins "Your shows" coverage: new season, trailer, renewal, cancellation, cast. For SEEN films, report sequel, spin-off and franchise news. Say when a MY LIST title arrives on a Dutch streamer or in cinemas. Never suggest any listed title again; steer picks away from NOT FOR ME. A NOT SURE title may come back once after 30 days, with a different angle on why he would like it. Rows that do not decrypt are junk: ignore them. If `taps.txt` is missing, the Sheet could not be read: say so in your report.

**sport** (`--a-sport`): F1 (results, standings, technical news; add a "Tech desk · for the SF-26
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
     Tomatometer %, Popcornmeter %, one-word verdict. Rotten Tomatoes pages load their scores with
     JavaScript, so a WebFetch of rottentomatoes.com returns no numbers (tested 21 Oct 2026): do not
     try it. Instead: for a new release, WebSearch "<title> Rotten Tomatoes score" and WebFetch a news
     report from the results that quotes it (say "via <outlet>"); for an older film, WebSearch
     "<title> <year> film Wikipedia" and WebFetch the article, whose Reception section gives the
     Tomatometer ("98% of 136 critics' reviews are positive"). Never invent a score; write "n/a" if
     none found. Picks get an "rt" only from one of these two routes.
   - **Coming soon**: next releases in his lanes with Netherlands cinema date (Pathé/Vue
     Amsterdam, original version) and France date for French films; streaming premieres with
     platform (Netflix, Disney+, Prime Video, Max).
   - **Your shows**: any news on his shows (new season, episode, trailer, cast, renewal). If
     nothing, skip it rather than pad.
   - **Tonight's pick + My list** (always last): 5 picks he probably has not seen, best first,
     matched to his taste (comedy like B99 and Modern Family, adult animation like Rick and Morty,
     legal drama like Suits, Star Wars, Marvel, great animation films), with where to stream in the
     Netherlands and why in one line. "where" must be checked: WebSearch "binge.nl <title>" (or
     "tvgids.nl <title>") and WebFetch the result, which lists the Dutch services (Netflix, Videoland,
     NPO Start, Prime Video, Pathé Thuis...). Write the picks as a plain JSON list to `parts/picks.json` (objects with t, y, kind, where, rt, why, img, link, wiki, yt, about; apostrophes are fine, `kit/assemble.py` builds the pick box, the My list box and all the escaping) and put the single marker `<!--PICKS-->` in `parts/screen.html` where the box goes, last. His phone shows one pick at a time with "Seen it / Not for me / + My list" buttons, remembers the taps and keeps his list. You cannot see those taps, so never repeat a title in the do-not-repeat digest `issues/<id>/history.txt` (last 30 issues) and honour the SEEN, MY LIST and NOT FOR ME lists in `issues/<id>/taps.txt`. Only give an "rt" you verified. Sunday: 8 picks.
   Posters (always try; they make it tempting):
   - Picks: add `"wiki": "tv|Show name"` for series (TVmaze, real portrait posters) or
     `"wiki": "en|Wikipedia_title"` for films; or `"img": "<poster URL>"` if you found one.
   - Coming soon: a `<div class="pgrid blk">` of up to 6 `<figure class="poster" data-pwiki="en|Film_title;fr|Titre_du_film" data-t="Title"><figcaption><b>21 Oct</b>Title</figcaption></figure>`
     per block (several specs separated by `;` are tried in order; only portrait images count, so
     logos and title cards are skipped). Unreleased films often have no Wikipedia poster yet: then
     find the official poster in a news article or studio page (WebFetch, ask for the og:image or
     poster URL) and add `data-src="<url>"`. A film with nothing gets a coloured title tile.
   **Trailer and info overlay** (Paul taps a Coming soon poster or a pick and gets a full-screen
   sheet with poster, facts, synopsis and the trailer playing inside the paper; the code is
   `docs/screen-overlay.js`, nothing to build). Feed it for EVERY Coming soon poster and EVERY pick:
   - Trailer: a YouTube video id (the 11 characters after `v=`). REQUIRED for every Coming soon
     poster and every pick: the trailer plays embedded inside the paper, and a missing id is a
     visible gap (17 Oct 2026 shipped with none). How to find it: WebSearch "<title> <year> official
     trailer"; WebSearch results rarely show YouTube URLs, so WebFetch a news article that embeds the
     trailer (Dark Horizons, Cartoon Brew, The Playlist, Empire, Awards Radar, ComingSoon) with the
     prompt "List every YouTube video id or youtube.com/embed or watch URL in this page, verbatim".
     Prefer the studio's or streamer's official channel (Disney, Pixar, Netflix, Marvel, Sony
     Pictures, Universal, Paramount, Warner Bros., LAIKA, Pathé, Gaumont...), the latest main
     trailer, the English original version (French films: the French trailer). The id counts as
     verified when it is copied verbatim from an embed in an article about that exact trailer (the
     article names the film and the trailer, and ideally the channel). Do NOT WebFetch the YouTube
     oEmbed, embed or watch URL: a hand-built youtube.com address needs a manual approval that nobody
     can give during a scheduled run (21 Oct 2026), and the embed page needs JavaScript anyway.
     Never invent an id. Only if no article embeds an official trailer, leave it out and the sheet
     offers a YouTube search button instead.
     Safety (since 21 Oct 2026): `docs/screen-overlay.js` checks each id on Paul's phone. A dead
     thumbnail or a YouTube player error 2, 5 or 100 swaps it for the search button; error 101, 150
     or 153 (owner disabled embedding) swaps it for a "Plays on YouTube only" link. So an id taken
     from an official embed never shows a broken box.
   - Videos in tap-for-more sheets (`<div class="vid" data-yt="<id>">`) use the same method: add one
     to every big story that has an official video (trailer, press conference, onboard lap, launch).
   - Synopsis: 2 to 3 sentences of your own, no spoilers beyond the first act.
   - Poster markup: add `data-yt="<id>" data-about="<synopsis>" data-meta="Animation · Pixar · 1h 42"
     data-where="Pathé Tuschinski and Vue, original version"` (for streaming: the platform and time).
     Runtime only when announced.
   - Picks: add `"yt": "<id>", "about": "<synopsis>"` to each pick object.
   Without `about`, the sheet fetches a summary live (TVmaze for `tv|`, otherwise Wikipedia), so
   always keep a good `data-pwiki` / `"wiki"` too.
   Photos: posters, stills and trailer frames from studio pages or news articles (route 1 or 2 in
   Photos). Sunday: add the weekend box office top 5 (worldwide if out, else US) and all trailers released that week.
