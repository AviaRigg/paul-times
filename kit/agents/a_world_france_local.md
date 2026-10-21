# Brief: World, France, Local

First read `kit/agents/_common.md`. You write: `parts/world.html`, `parts/france.html`, `parts/local.html`

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
4. **local** (`--a-local`): full Annecy and Haute-Savoie coverage, including the small local stories
   (police, firefighters, council, sport, events): Paul wants them all, they are not filler. Annecy and Haute-Savoie lead with a photo of the place, the live weather box
   (step 4), 3 to 4 Annecy briefs, **Dutch word of the day** (word, pronunciation,
   example sentence, bonus phrase; useful for a delivery driver).

## Weather box (Local)

the weather box is LIVE. Paul's phone fetches Open-Meteo when he
   opens the issue and renders the Amsterdam rain-gear verdict (YES / pack it / no), hourly
   strip, wind for the scooter, what to wear, dark-from time, 3 days, and Annecy. The box must
   be `<div class="box wxl blk" data-wx><h4>Weather</h4> ...printed fallback... </div>`.
   The printed fallback is only shown if the live fetch fails: research it with WebSearch
   (for example "yr.no Amsterdam forecast", then WebFetch the page), give today's Amsterdam
   rain verdict in one line ("Rain gear: yes, showers 14:00 to 18:00"), today plus 3 days for
   both cities. NEVER copy weather from a previous issue; if nothing can be read, the fallback
   is just "Live forecast loads when you open the issue." Do not write a separate
   "Scooter check" paragraph; the live box covers it.
