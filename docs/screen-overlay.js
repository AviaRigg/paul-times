/* The Paul Times: tap-for-more overlay (whole paper).
   Tap any story, brief or feature box and a full-screen sheet opens with the deeper version.
   Tap a Screen poster or Tonight's pick for poster, facts, synopsis and the trailer.
   Loaded by every issue (kit/template.html, and injected by docs/index.html for older issues). It only
   uses event delegation and data attributes, never the template's private functions.

   STORIES (written by the morning run, see RUNBOOK.md "Tap for more"):
     Put <template class="more"> ... </template> as the LAST child of a .brief, .head (big story), .box or .fun.
     Tapping the block, or any paragraph / In brief / pull quote of that big story, opens it.
     Another block can point at it: <div class="head blk kn" data-more="world-lead"> + <template class="more" data-id="world-lead">.
     Inside the template: <p>, <h5> subheads, <ul>, <ol class="tl">, <div class="tbl"><table>, <figure class="photo" data-src|data-wiki>,
     <div class="vid" data-yt="ID"><span>caption</span></div>, <div class="you">Why it matters to you</div>,
     <div class="srcs"><a href="..">Source</a> ...</div>. Optional data-title on the template overrides the headline.
   Briefs and big-story headlines without a template still open: their own text, the links in them, and a news search.

   SCREEN: <figure class="poster" data-pwiki data-t data-yt data-about data-meta data-where data-link> and picks {"yt","about"}.
   No synopsis: fetched live (TVmaze for "tv|", otherwise Wikipedia). No trailer: a YouTube search button. */
(function () {
  if (window.__tptOverlay) return; window.__tptOverlay = true;
  const FR = (() => { try { return (JSON.parse(localStorage.getItem('tpt-settings')) || {}).lang === 'fr'; } catch (e) { return false; } })();
  const L = (en, fr) => FR ? fr : en;
  const esc = x => String(x == null ? '' : x).replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
  const ytId = s => { s = String(s || '').trim(); const m = s.match(/(?:v=|youtu\.be\/|embed\/|shorts\/)([\w-]{11})/); return m ? m[1] : (/^[\w-]{11}$/.test(s) ? s : ''); };
  const txt = el => (el ? el.textContent : '').replace(/\s+/g, ' ').trim();

  const css = `
.pgrid .poster { position: relative; cursor: pointer; -webkit-tap-highlight-color: transparent; }
.pgrid .poster::before { content: "▶"; position: absolute; top: 6px; right: 6px; z-index: 1; width: 24px; height: 24px; border-radius: 50%;
  background: rgba(0,0,0,.62); color: #fff; font-size: 10px; line-height: 24px; text-align: center; padding-left: 2px; box-sizing: border-box; pointer-events: none; }
.pgrid .poster:active { transform: scale(.97); }
.pick .pwrap { cursor: pointer; -webkit-tap-highlight-color: transparent; }
.pick .ptxt::after { content: "${L('▶ Trailer and info', '▶ Bande-annonce et infos')}"; display: inline-block; margin-top: 4px; font-size: 12px; font-weight: 700;
  letter-spacing: .04em; color: var(--accent); border: 1.5px solid var(--accent); border-radius: 14px; padding: 3px 10px; }
template.more { display: none; }
.tov-t { cursor: pointer; -webkit-tap-highlight-color: transparent; }
.tov-t:active { opacity: .7; }
.brief:has(> template.more) h4::after, .box:has(> template.more) h4::after, .fun:has(> template.more) .lbl::after,
.head:has(> template.more) h3::after, .head[data-more] h3::after {
  content: " ${L('More', 'Plus')} ›"; color: var(--accent); font-family: var(--body); font-size: 12px; font-weight: 700; letter-spacing: .1em;
  text-transform: uppercase; white-space: nowrap; vertical-align: middle; }
.box.inv:has(> template.more) h4::after { color: inherit; opacity: .85; }
#tov { position: fixed; inset: 0; z-index: 9000; background: rgba(0,0,0,.55); opacity: 0; transition: opacity .22s; }
#tov.on { opacity: 1; }
#tov .sheet { position: absolute; left: 0; right: 0; bottom: 0; top: calc(env(safe-area-inset-top, 0px) + 10px); background: var(--bg); color: var(--ink);
  border-radius: 14px 14px 0 0; overflow-y: auto; overflow-x: hidden; -webkit-overflow-scrolling: touch; overscroll-behavior: contain; transform: translateY(100%);
  transition: transform .28s cubic-bezier(.2,.8,.2,1); padding-bottom: calc(env(safe-area-inset-bottom, 0px) + 28px); font-size: 17px; line-height: 1.5; }
#tov.on .sheet { transform: none; }
#tov .grab { position: sticky; top: 0; z-index: 2; display: flex; justify-content: space-between; align-items: center; padding: 10px 14px 4px 18px;
  background: var(--bg); border-bottom: 3px solid var(--accent); font-size: 11px; letter-spacing: .16em; text-transform: uppercase; font-weight: 700; color: var(--accent); }
#tov .grab::before { content: ""; position: absolute; top: 4px; left: 50%; width: 38px; height: 4px; margin-left: -19px; border-radius: 2px; background: var(--rule); }
#tov .x { font: inherit; font-size: 26px; line-height: 1; width: 40px; height: 40px; border: 0; background: transparent; color: var(--ink); cursor: pointer; margin-right: -8px; }
#tov .in { padding: 14px 18px 0; }
#tov .in > * + * { margin-top: 12px; }
#tov .hero { display: flex; gap: 14px; align-items: flex-start; }
#tov .hero .pst { width: 38%; flex: none; aspect-ratio: 2 / 3; object-fit: cover; border-radius: 3px; background: var(--card); display: block; box-shadow: 0 4px 14px rgba(0,0,0,.25); }
#tov .hero .pst.ph { background: var(--accent); color: #fff; display: flex; align-items: center; justify-content: center; text-align: center; padding: 8px;
  box-sizing: border-box; font-family: var(--display); font-size: 17px; line-height: 1.15; }
#tov .hero .ht { flex: 1; min-width: 0; }
#tov .kick { font-size: 11px; letter-spacing: .14em; text-transform: uppercase; color: var(--accent); font-weight: 700; }
#tov h2 { font-family: var(--display); font-size: 28px; line-height: 1.1; margin: 4px 0 0; }
#tov .hero h2 { font-size: 27px; margin-bottom: 8px; }
#tov .when { font-family: var(--display); font-size: 19px; font-weight: 700; margin: 0 0 4px; }
#tov .meta { font-size: 13.5px; color: var(--muted); margin: 0 0 4px; line-height: 1.4; }
#tov .trailer, #tov .vid { margin-left: -18px; margin-right: -18px; background: #000; aspect-ratio: 16 / 9; position: relative; }
#tov .vid { margin-bottom: 28px; }
#tov .vid > span { position: absolute; top: 100%; left: 18px; right: 18px; font-size: 13px; color: var(--muted); font-style: italic; padding-top: 4px; line-height: 1.3; }
#tov .trailer iframe, #tov .vid iframe { position: absolute; inset: 0; width: 100%; height: 100%; border: 0; }
#tov .trailer.none { display: flex; align-items: center; justify-content: center; text-decoration: none; color: #fff; flex-direction: column; gap: 8px;
  background: linear-gradient(135deg, var(--accent), #000); }
#tov .trailer.none .pl { width: 58px; height: 58px; border-radius: 50%; background: rgba(255,255,255,.18); display: flex; align-items: center; justify-content: center; font-size: 22px; padding-left: 4px; box-sizing: border-box; }
#tov .trailer.none span { font-size: 14px; font-weight: 700; }
#tov .yt { display: block; font-size: 12.5px; color: var(--muted); margin: 6px 0 0; text-align: right; }
#tov h4, #tov h5 { font-family: var(--display); font-size: 19px; margin: 20px 0 0; border-top: 1px solid var(--rule); padding-top: 10px; line-height: 1.25; }
#tov h5 + * { margin-top: 4px; }
#tov p { margin: 0; }
#tov p.txt, #tov .body p { font-size: 17px; }
#tov .body > p + p { margin-top: 10px; }
#tov .body ul { margin: 6px 0 0; padding-left: 20px; }
#tov .body ul li { margin: 4px 0; }
#tov .body ul li::marker { color: var(--accent); }
#tov .orig { background: var(--card); border-top: 2px solid var(--ink); padding: 10px 12px; font-size: 16px; }
#tov .orig p + p { margin-top: 6px; }
#tov .you { border: 2px solid var(--accent); padding: 10px 12px; font-size: 16px; }
#tov .you::before { content: "${L('Why it matters to you', 'Pourquoi ça te concerne')}"; display: block; font-size: 11px; letter-spacing: .14em; text-transform: uppercase; font-weight: 700; color: var(--accent); margin-bottom: 4px; }
#tov .why { border-left: 3px solid var(--accent); padding: 2px 0 2px 12px; font-style: italic; }
#tov .src, #tov .srcs { font-size: 13px; color: var(--muted); }
#tov .srcs { border-top: 1px solid var(--rule); padding-top: 10px; margin-top: 22px; }
#tov .srcs::before { content: "${L('Sources', 'Sources')}"; display: block; font-size: 11px; letter-spacing: .14em; text-transform: uppercase; font-weight: 700; margin-bottom: 4px; }
#tov .srcs a { display: block; color: var(--accent); padding: 5px 0; text-decoration: none; font-weight: 600; }
#tov .srcs a::after { content: " ›"; }
#tov .facts { list-style: none; padding: 0; margin: 4px 0 0; font-size: 15px; }
#tov .facts li { padding: 5px 0; border-bottom: 1px solid var(--rule); display: flex; justify-content: space-between; gap: 12px; }
#tov .facts li b { font-weight: 600; color: var(--muted); }
#tov .facts li span { text-align: right; }
#tov figure.photo { margin-left: -18px; margin-right: -18px; }
#tov figure.photo figcaption { padding: 4px 18px 0; font-size: 13.5px; color: var(--muted); }
#tov figure.photo.portrait { margin: 0; }
#tov .btns { display: grid; grid-template-columns: 1fr 1fr; gap: 6px; margin-top: 18px; }
#tov .btns button { font: inherit; font-size: 14px; font-weight: 700; padding: 11px 4px; border: 1.5px solid var(--ink); background: var(--bg); color: var(--ink); border-radius: 3px; cursor: pointer; }
#tov .btns button.add { background: var(--accent); border-color: var(--accent); color: #fff; }
#tov a.more { display: block; margin-top: 18px; padding: 12px; text-align: center; border: 1.5px solid var(--accent); border-radius: 3px; font-size: 14px; color: var(--accent); font-weight: 700; text-decoration: none; }
#tov .loading { color: var(--muted); font-size: 14px; font-style: italic; }
#tov .note { font-size: 13px; color: var(--muted); font-style: italic; }
`;
  const st = document.createElement('style'); st.textContent = css; document.head.appendChild(st);

  // ---------- sheet shell ----------
  let ov = null, lastFocus = null;
  function close() {
    if (!ov) return; const o = ov; ov = null;
    o.querySelectorAll('iframe').forEach(f => f.remove()); // stops any video
    o.classList.remove('on'); setTimeout(() => o.remove(), 280);
    if (lastFocus && lastFocus.focus) try { lastFocus.focus({ preventScroll: true }); } catch (e) {}
  }
  function sheet(kicker, accent, html, label) {
    close(); lastFocus = document.activeElement;
    const el = document.createElement('div'); el.id = 'tov';
    el.innerHTML = `<div class="sheet" role="dialog" aria-modal="true" aria-label="${esc(label || kicker)}"${accent ? ` style="--accent:${esc(accent)}"` : ''}>
      <div class="grab"><span>${esc(kicker)}</span><button class="x" aria-label="${L('Close', 'Fermer')}">×</button></div><div class="in">${html}</div></div>`;
    document.body.appendChild(el); ov = el;
    requestAnimationFrame(() => requestAnimationFrame(() => el.classList.add('on')));
    el.querySelector('.x').onclick = close;
    el.addEventListener('click', e => { if (e.target === el) close(); });
    const sh = el.querySelector('.sheet'); let y0 = null, dy = 0;
    sh.addEventListener('touchstart', e => { y0 = sh.scrollTop <= 0 ? e.touches[0].clientY : null; dy = 0; }, { passive: true });
    sh.addEventListener('touchmove', e => { if (y0 == null) return; dy = e.touches[0].clientY - y0; if (dy > 0) { sh.style.transition = 'none'; sh.style.transform = 'translateY(' + dy + 'px)'; } }, { passive: true });
    sh.addEventListener('touchend', () => { if (y0 == null) return; sh.style.transition = ''; sh.style.transform = ''; if (dy > 110) close(); y0 = null; });
    return el;
  }
  const embed = (id, title) => `<iframe src="https://www.youtube-nocookie.com/embed/${id}?playsinline=1&rel=0&modestbranding=1" title="${esc(title)}"
    allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; fullscreen" allowfullscreen referrerpolicy="strict-origin-when-cross-origin"></iframe>`;

  // photos and videos inside a sheet
  async function sheetPhoto(fig) {
    let src = fig.dataset.src, credit = fig.dataset.credit || '', link = fig.dataset.link || '';
    if (!src && fig.dataset.wiki) {
      const [lang, title] = fig.dataset.wiki.split('|');
      try {
        const r = await fetch('https://' + lang + '.wikipedia.org/w/api.php?action=query&format=json&origin=*&prop=pageimages&piprop=thumbnail&pithumbsize=900&pilicense=free&redirects=1&titles=' + encodeURIComponent(title));
        const p = Object.values(((await r.json()).query || {}).pages || {})[0];
        if (p && p.thumbnail) { src = p.thumbnail.source; credit = credit || 'Wikimedia Commons'; link = link || 'https://' + lang + '.m.wikipedia.org/wiki/' + encodeURIComponent(title); }
      } catch (e) {}
    }
    if (!src) return;
    const img = new Image(); img.className = 'ph-img'; img.alt = fig.dataset.alt || ''; img.referrerPolicy = 'no-referrer';
    img.onload = () => fig.classList.add('ready'); img.src = src; fig.insertBefore(img, fig.firstChild);
    const cap = fig.querySelector('figcaption') || fig.appendChild(document.createElement('figcaption'));
    const cr = document.createElement('span'); cr.className = 'credit'; cr.textContent = L('Image: ', 'Image : ') + (credit || L('source', 'source'));
    if (link) { const a = document.createElement('a'); a.href = link; a.target = '_blank'; a.rel = 'noopener'; a.textContent = L(' · open source ›', ' · voir la source ›'); cr.appendChild(a); }
    cap.appendChild(cr);
  }
  function wire(el) {
    el.querySelectorAll('.in figure.photo').forEach(f => sheetPhoto(f));
    el.querySelectorAll('.in .vid[data-yt]').forEach(v => { const id = ytId(v.dataset.yt); if (id) v.insertAdjacentHTML('afterbegin', embed(id, txt(v) || 'Video')); else v.remove(); });
    el.querySelectorAll('.in a[href]').forEach(a => { a.target = '_blank'; a.rel = 'noopener'; });
  }

  // ---------- stories ----------
  const accentOf = el => { try { return getComputedStyle(el).getPropertyValue('--accent').trim(); } catch (e) { return ''; } };
  const sectionName = el => { const pg = el.closest('.page'); const w = pg && pg.querySelector('.ph .where'); return txt(w) || L('More', 'Plus'); };
  const tplOf = blk => { if (!blk) return null; const own = [...blk.children].find(c => c.matches('template.more')); if (own) return own; const id = blk.dataset && blk.dataset.more;
    return id ? document.querySelector('template.more[data-id="' + CSS.escape(id) + '"]') : null; };
  const BLOCKED = 'a, button, input, textarea, select, label, iframe, .sdk, .pick, .mylist, .wxl, [data-wx], .pgrid, .checked, .feedback, #toc, .toc, .jump, .pf, .ph, [data-goto]';
  // which block owns a tap: the block itself if it has a template, or the big story it belongs to (paragraphs, In brief, pull quote)
  function ownerOf(blk) {
    if (blk.matches('.brief, .head, .box, .fun') || tplOf(blk)) return blk;
    if (!blk.matches('p, .inbrief, .pull')) return null;
    const all = [...document.querySelectorAll('#reader .page .blk')]; let i = all.indexOf(blk);
    const page = blk.closest('.page'), key = page && page.dataset.key;
    while (--i >= 0) {
      const b = all[i], bp = b.closest('.page');
      if (bp && key && bp.dataset.key !== key) return null;
      if (b.matches('.head')) return tplOf(b) ? b : null;
      if (b.matches('.brief, .box, .fun, .opener, .pgrid, .pick, .sdk, .tl')) return null;
    }
    return null;
  }
  function openStory(owner) {
    const tpl = tplOf(owner);
    const kicker = txt(owner.querySelector('.kicker')) || sectionName(owner);
    const head = (tpl && tpl.dataset.title) || txt(owner.querySelector('h3, h4, .lbl')) || '';
    let body;
    if (tpl) body = `<div class="body">${tpl.innerHTML}</div>`;
    else {
      // no deeper version printed: show the story's own text, its links and a news search
      const parts = [];
      if (owner.matches('.head')) { let n = owner.closest('.blk'); const all = [...document.querySelectorAll('#reader .page .blk')]; let i = all.indexOf(n);
        while (++i < all.length && parts.length < 3) { const b = all[i]; if (b.matches('.head, .brief, .box, .fun, .opener')) break; if (b.matches('.inbrief, p')) parts.push(b); } }
      else parts.push(...owner.querySelectorAll(':scope > p'));
      const seen = new Set(), links = [...owner.querySelectorAll('a[href^="http"]')].concat(...parts.map(p => [...p.querySelectorAll('a[href^="http"]')]))
        .filter(a => !seen.has(a.href) && seen.add(a.href));
      const q = encodeURIComponent(head);
      body = (parts.length ? `<div class="orig">${parts.map(p => `<p>${p.innerHTML}</p>`).join('')}</div>` : '')
        + (links.length ? `<div class="srcs">${links.map(a => `<a href="${esc(a.href)}">${esc(txt(a) || a.hostname)}</a>`).join('')}</div>` : '')
        + `<p class="note">${L('No deeper version of this story in this issue.', 'Pas de version longue pour ce sujet dans ce numéro.')}</p>`
        + `<a class="more" href="https://news.google.com/search?q=${q}&hl=${FR ? 'fr&gl=FR&ceid=FR:fr' : 'en-GB&gl=GB&ceid=GB:en'}">${L('Follow this story in the news ›', 'Suivre ce sujet dans l\'actualité ›')}</a>`;
    }
    const el = sheet(kicker, accentOf(owner), `${head ? `<h2>${esc(head)}</h2>` : ''}${body}`, head);
    wire(el);
  }

  // ---------- screen: posters and picks ----------
  async function liveInfo(specs, title) {
    const ck = 'tpt-ovinfo1-' + (FR ? 'fr-' : '') + (specs || title);
    try { const c = JSON.parse(localStorage.getItem(ck)); if (c && Date.now() - c.at < 6048e5) return c.v; } catch (e) {}
    let list = String(specs || '').split(';').filter(Boolean).map(s => s.split('|'));
    if (!list.length && title) list = [['en', title]];
    if (FR) list.sort((a, b) => (b[0] === 'fr') - (a[0] === 'fr'));
    let v = null;
    for (const [src, q] of list) {
      try {
        if (src === 'tv') {
          const r = await fetch('https://api.tvmaze.com/singlesearch/shows?q=' + encodeURIComponent(q)); if (!r.ok) continue;
          const j = await r.json();
          v = { text: String(j.summary || '').replace(/<[^>]+>/g, '').trim(), source: 'TVmaze', link: j.url, facts: [
            [L('Genre', 'Genre'), (j.genres || []).join(', ')],
            [L('Channel', 'Chaîne'), (j.network && j.network.name) || (j.webChannel && j.webChannel.name) || ''],
            [L('Premiered', 'Première'), j.premiered ? new Date(j.premiered + 'T12:00:00').toLocaleDateString(FR ? 'fr-FR' : 'en-GB', { day: 'numeric', month: 'short', year: 'numeric' }) : ''],
            [L('Status', 'Statut'), j.status === 'Running' ? L('Still running', 'En cours') : j.status === 'Ended' ? L('Ended', 'Terminée') : (j.status || '')],
            [L('Episode length', 'Durée'), j.averageRuntime ? j.averageRuntime + ' min' : ''],
            [L('Viewer rating', 'Note du public'), j.rating && j.rating.average ? j.rating.average + ' / 10' : '']
          ].filter(f => f[1]) };
        } else {
          const r = await fetch('https://' + src + '.wikipedia.org/api/rest_v1/page/summary/' + encodeURIComponent(q.replace(/ /g, '_')) + '?redirect=true');
          if (!r.ok) continue;
          const j = await r.json(); if (j.type === 'disambiguation' || !j.extract) continue;
          v = { text: j.extract, source: 'Wikipedia', link: j.content_urls && j.content_urls.mobile && j.content_urls.mobile.page, facts: [] };
        }
        if (v && v.text) break;
      } catch (e) {}
    }
    try { if (v) localStorage.setItem(ck, JSON.stringify({ at: Date.now(), v })); } catch (e) {}
    return v;
  }
  function openTitle(d) {
    const id = ytId(d.yt);
    const q = encodeURIComponent([d.t, d.y, FR ? 'bande annonce' : 'official trailer'].filter(Boolean).join(' '));
    const trailer = id
      ? `<div class="trailer">${embed(id, d.t + ' trailer')}</div><a class="yt" href="https://www.youtube.com/watch?v=${id}" target="_blank" rel="noopener">${L('Not playing? Open in YouTube ›', 'Ne se lance pas ? Ouvrir dans YouTube ›')}</a>`
      : `<a class="trailer none" href="https://www.youtube.com/results?search_query=${q}" target="_blank" rel="noopener"><div class="pl">▶</div><span>${L('Find the trailer on YouTube', 'Trouver la bande-annonce sur YouTube')}</span></a>`;
    const facts = (d.facts || []).filter(f => f[1]);
    const el = sheet(d.kicker, d.accent, `
        <div class="hero">${d.img ? `<img class="pst" src="${esc(d.img)}" alt="${esc(d.t)} poster" referrerpolicy="no-referrer">` : `<div class="pst ph">${esc(d.t)}</div>`}
          <div class="ht">${d.when ? `<p class="when">${esc(d.when)}</p>` : ''}<h2>${esc(d.t)}</h2>${d.meta ? `<p class="meta">${esc(d.meta)}</p>` : ''}${d.where ? `<p class="meta"><b>${L('Where', 'Où')}:</b> ${esc(d.where)}</p>` : ''}</div>
        </div>
        ${trailer}
        ${d.why ? `<h4>${L('Why you', 'Pourquoi toi')}</h4><p class="txt why">${esc(d.why)}</p>` : ''}
        <h4>${L('The story', 'L\'histoire')}</h4><div class="about">${d.about ? `<p class="txt">${esc(d.about)}</p>` : `<p class="loading">${L('Loading…', 'Chargement…')}</p>`}</div>
        <div class="fx">${facts.length ? `<ul class="facts">${facts.map(f => `<li><b>${esc(f[0])}</b><span>${esc(f[1])}</span></li>`).join('')}</ul>` : ''}</div>
        ${d.buttons ? `<div class="btns">${d.buttons}</div>` : ''}
        ${d.link ? `<a class="more" href="${esc(d.link)}" target="_blank" rel="noopener">${L('More ›', 'En savoir plus ›')}</a>` : ''}`, d.t);
    const img = el.querySelector('img.pst'); if (img) img.onerror = () => { const ph = document.createElement('div'); ph.className = 'pst ph'; ph.textContent = d.t; img.replaceWith(ph); };
    el.querySelectorAll('.btns button[data-a]').forEach(b => b.onclick = () => { const t = d.card && d.card.querySelector('.btns button[data-a="' + b.dataset.a + '"]'); close(); if (t) t.click(); });
    if (!d.about) liveInfo(d.specs, d.t).then(v => {
      if (ov !== el) return;
      const a = el.querySelector('.about');
      if (!v || !v.text) { a.innerHTML = `<p class="txt" style="color:var(--muted)">${L('No synopsis yet. The trailer is the best preview for now.', 'Pas encore de synopsis. La bande-annonce reste le meilleur aperçu.')}</p>`; return; }
      a.innerHTML = `<p class="txt">${esc(v.text)}</p><p class="src">${L('Source', 'Source')}: ${v.link ? `<a href="${esc(v.link)}" target="_blank" rel="noopener" style="color:inherit">${esc(v.source)}</a>` : esc(v.source)}</p>`;
      if (!facts.length && v.facts && v.facts.length) el.querySelector('.fx').innerHTML = `<ul class="facts">${v.facts.map(f => `<li><b>${esc(f[0])}</b><span>${esc(f[1])}</span></li>`).join('')}</ul>`;
    });
  }
  function fromPoster(fig) {
    const ds = fig.dataset, img = fig.querySelector('img.pp'), b = fig.querySelector('figcaption b');
    return { kicker: L('Coming soon', 'Bientôt'), accent: accentOf(fig), t: ds.t || txt(fig.querySelector('figcaption')),
      when: b ? txt(b) : '', meta: ds.meta || '', where: ds.where || '', about: ds.about || '', yt: ds.yt || '',
      img: img ? img.src : (ds.src || ''), specs: ds.pwiki || '', link: ds.link || '', y: ds.y || '' };
  }
  function fromPick(card) {
    let picks = []; try { picks = JSON.parse(card.dataset.pick); } catch (e) {}
    const t = txt(card.querySelector('h4')); const p = picks.find(x => x.t === t); if (!p) return null;
    const img = card.querySelector('.pimg');
    const lab = [['seen', L('✓ Seen it', '✓ Déjà vu')], ['list', L('+ My list', '+ Ma liste'), 'add'], ['later', L('? Not sure', '? Pas sûr')], ['no', L('✗ Not for me', '✗ Pas pour moi')]];
    return { kicker: L("Tonight's pick", 'À voir ce soir'), accent: accentOf(card), t: p.t, y: p.y, meta: [p.kind, p.y, p.rt ? 'Rotten Tomatoes ' + p.rt : ''].filter(Boolean).join(' · '),
      where: p.where || '', why: p.why || '', about: p.about || '', yt: p.yt || p.trailer || '', img: img && !img.hidden && img.src ? img.src : (p.img || ''),
      specs: p.wiki || '', link: p.link || '', card, buttons: lab.map(x => `<button data-a="${x[0]}"${x[2] ? ' class="add"' : ''}>${x[1]}</button>`).join('') };
  }

  // ---------- taps ----------
  document.addEventListener('click', e => {
    const t = e.target; if (!t || !t.closest || (ov && ov.contains(t))) return;
    if (!t.closest('#reader')) return;
    const fig = t.closest('.pgrid .poster'); if (fig) { e.preventDefault(); openTitle(fromPoster(fig)); return; }
    const pw = t.closest('.pick .pwrap'); if (pw) { const d = fromPick(pw.closest('.pick')); if (d) { e.preventDefault(); openTitle(d); } return; }
    if (t.closest(BLOCKED)) return;
    if (window.getSelection && String(window.getSelection()).length) return; // selecting text, not tapping
    let blk = t.closest('.blk'); if (!blk) return;
    // a box without a deeper version stays a plain box (tables, scoreboards)
    const owner = ownerOf(blk); if (!owner) return;
    if (owner.matches('.box, .fun') && !tplOf(owner)) return;
    e.preventDefault(); openStory(owner);
  });
  // mark tappable blocks so they show a pressed state (re-run after the paper re-paginates)
  function mark() { document.querySelectorAll('#reader .blk').forEach(b => { const o = (() => { try { return ownerOf(b); } catch (e) { return null; } })();
    if (o && !(o.matches('.box, .fun') && !tplOf(o))) b.classList.add('tov-t'); }); }
  let mt = 0; new MutationObserver(() => { clearTimeout(mt); mt = setTimeout(mark, 300); }).observe(document.body, { childList: true, subtree: true });
  mark();
  document.addEventListener('keydown', e => { if (e.key === 'Escape') close(); });
})();
