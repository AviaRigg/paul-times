/* The Paul Times: Screen overlay.
   Tap a "Coming soon" poster or a "Tonight's pick" card to open a full-screen sheet with the poster,
   facts, synopsis and an embedded YouTube trailer.
   Loaded by every issue (kit/template.html, and injected by docs/index.html for older issues), so it
   only uses event delegation and data attributes, never the template's private functions.

   Data the morning run can add (all optional, see RUNBOOK.md, Screen):
     Poster:  <figure class="poster" data-pwiki=".." data-t="Title" data-yt="YouTubeID" data-about="2 to 3 sentences"
                      data-meta="Animation · Pixar · 1h 42" data-where="Pathé, original version" data-link="https://..">
     Pick:    {"t":..,"yt":"YouTubeID","about":"2 to 3 sentences", ...}
   Missing synopsis: fetched live (TVmaze for "tv|" specs, Wikipedia summary otherwise).
   Missing trailer: a button that opens a YouTube search. */
(function () {
  if (window.__tptOverlay) return; window.__tptOverlay = true;
  const FR = (() => { try { return (JSON.parse(localStorage.getItem('tpt-settings')) || {}).lang === 'fr'; } catch (e) { return false; } })();
  const L = (en, fr) => FR ? fr : en;
  const esc = x => String(x == null ? '' : x).replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
  const ytId = s => { s = String(s || '').trim(); const m = s.match(/(?:v=|youtu\.be\/|embed\/|shorts\/)([\w-]{11})/); return m ? m[1] : (/^[\w-]{11}$/.test(s) ? s : ''); };

  const css = `
.pgrid .poster { position: relative; cursor: pointer; -webkit-tap-highlight-color: transparent; }
.pgrid .poster::before { content: "▶"; position: absolute; top: 6px; right: 6px; z-index: 1; width: 24px; height: 24px; border-radius: 50%;
  background: rgba(0,0,0,.62); color: #fff; font-size: 10px; line-height: 24px; text-align: center; padding-left: 2px; box-sizing: border-box; pointer-events: none; }
.pgrid .poster:active { transform: scale(.97); }
.pick .pwrap { cursor: pointer; -webkit-tap-highlight-color: transparent; }
.pick .ptxt::after { content: "${L('▶ Trailer and info', '▶ Bande-annonce et infos')}"; display: inline-block; margin-top: 4px; font-size: 12px; font-weight: 700;
  letter-spacing: .04em; color: var(--accent); border: 1.5px solid var(--accent); border-radius: 14px; padding: 3px 10px; }
#tov { position: fixed; inset: 0; z-index: 9000; background: rgba(0,0,0,.55); opacity: 0; transition: opacity .22s; }
#tov.on { opacity: 1; }
#tov .sheet { position: absolute; left: 0; right: 0; bottom: 0; top: calc(env(safe-area-inset-top, 0px) + 10px); background: var(--bg); color: var(--ink);
  border-radius: 14px 14px 0 0; overflow-y: auto; -webkit-overflow-scrolling: touch; overscroll-behavior: contain; transform: translateY(100%);
  transition: transform .28s cubic-bezier(.2,.8,.2,1); --accent: var(--a-screen); padding-bottom: calc(env(safe-area-inset-bottom, 0px) + 24px); }
#tov.on .sheet { transform: none; }
#tov .grab { position: sticky; top: 0; z-index: 2; display: flex; justify-content: space-between; align-items: center; padding: 8px 14px 8px 18px;
  background: var(--bg); border-bottom: 3px solid var(--accent); font-size: 11px; letter-spacing: .16em; text-transform: uppercase; font-weight: 700; color: var(--accent); }
#tov .grab::before { content: ""; position: absolute; top: 4px; left: 50%; width: 38px; height: 4px; margin-left: -19px; border-radius: 2px; background: var(--rule); }
#tov .x { font: inherit; font-size: 26px; line-height: 1; width: 40px; height: 40px; border: 0; background: transparent; color: var(--ink); cursor: pointer; margin-right: -8px; }
#tov .in { padding: 14px 18px 0; }
#tov .hero { display: flex; gap: 14px; align-items: flex-start; }
#tov .hero .pst { width: 38%; flex: none; aspect-ratio: 2 / 3; object-fit: cover; border-radius: 3px; background: var(--card); display: block; box-shadow: 0 4px 14px rgba(0,0,0,.25); }
#tov .hero .pst.ph { background: var(--accent); color: #fff; display: flex; align-items: center; justify-content: center; text-align: center; padding: 8px;
  box-sizing: border-box; font-family: var(--display); font-size: 17px; line-height: 1.15; }
#tov .hero .ht { flex: 1; min-width: 0; }
#tov .kick { font-size: 11px; letter-spacing: .14em; text-transform: uppercase; color: var(--accent); font-weight: 700; }
#tov h2 { font-family: var(--display); font-size: 27px; line-height: 1.08; margin: 4px 0 8px; }
#tov .when { font-family: var(--display); font-size: 19px; font-weight: 700; margin: 0 0 4px; }
#tov .meta { font-size: 13.5px; color: var(--muted); margin: 0 0 4px; line-height: 1.4; }
#tov .trailer { margin: 16px -18px 0; background: #000; aspect-ratio: 16 / 9; position: relative; }
#tov .trailer iframe { position: absolute; inset: 0; width: 100%; height: 100%; border: 0; }
#tov .trailer.none { display: flex; align-items: center; justify-content: center; text-decoration: none; color: #fff; flex-direction: column; gap: 8px;
  background: linear-gradient(135deg, var(--accent), #000); }
#tov .trailer.none .pl { width: 58px; height: 58px; border-radius: 50%; background: rgba(255,255,255,.18); display: flex; align-items: center; justify-content: center; font-size: 22px; padding-left: 4px; box-sizing: border-box; }
#tov .trailer.none span { font-size: 14px; font-weight: 700; }
#tov .yt { display: block; font-size: 12.5px; color: var(--muted); margin: 6px 0 0; text-align: right; }
#tov h4 { font-family: var(--display); font-size: 18px; margin: 18px 0 4px; border-top: 1px solid var(--rule); padding-top: 10px; }
#tov p.txt { font-size: 16.5px; margin: 0; }
#tov .why { border-left: 3px solid var(--accent); padding: 2px 0 2px 12px; font-style: italic; }
#tov .src { font-size: 12px; color: var(--muted); margin-top: 6px; }
#tov .facts { list-style: none; padding: 0; margin: 4px 0 0; font-size: 15px; }
#tov .facts li { padding: 5px 0; border-bottom: 1px solid var(--rule); display: flex; justify-content: space-between; gap: 12px; }
#tov .facts li b { font-weight: 600; color: var(--muted); }
#tov .facts li span { text-align: right; }
#tov .btns { display: grid; grid-template-columns: 1fr 1fr; gap: 6px; margin-top: 18px; }
#tov .btns button { font: inherit; font-size: 14px; font-weight: 700; padding: 11px 4px; border: 1.5px solid var(--ink); background: var(--bg); color: var(--ink); border-radius: 3px; cursor: pointer; }
#tov .btns button.add { background: var(--accent); border-color: var(--accent); color: #fff; }
#tov a.more { display: inline-block; margin-top: 14px; font-size: 14px; color: var(--accent); font-weight: 700; }
#tov .loading { color: var(--muted); font-size: 14px; font-style: italic; }
`;
  const st = document.createElement('style'); st.textContent = css; document.head.appendChild(st);

  // ---------- live info (cached on the phone for 7 days) ----------
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
          const text = String(j.summary || '').replace(/<[^>]+>/g, '').trim();
          v = { text, source: 'TVmaze', link: j.url, facts: [
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

  // ---------- the sheet ----------
  let ov = null, lastFocus = null;
  function close() {
    if (!ov) return; const o = ov; ov = null;
    o.querySelectorAll('iframe').forEach(f => f.remove()); // stops the video
    o.classList.remove('on'); setTimeout(() => o.remove(), 280);
    if (lastFocus && lastFocus.focus) try { lastFocus.focus({ preventScroll: true }); } catch (e) {}
  }
  function open(d) {
    close(); lastFocus = document.activeElement;
    const id = ytId(d.yt);
    const q = encodeURIComponent([d.t, d.y, FR ? 'bande annonce' : 'official trailer'].filter(Boolean).join(' '));
    const trailer = id
      ? `<div class="trailer"><iframe src="https://www.youtube-nocookie.com/embed/${id}?playsinline=1&rel=0&modestbranding=1" title="${esc(d.t)} trailer"
           allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; fullscreen" allowfullscreen
           referrerpolicy="strict-origin-when-cross-origin"></iframe></div>
         <a class="yt" href="https://www.youtube.com/watch?v=${id}" target="_blank" rel="noopener">${L('Not playing? Open in YouTube ›', 'Ne se lance pas ? Ouvrir dans YouTube ›')}</a>`
      : `<a class="trailer none" href="https://www.youtube.com/results?search_query=${q}" target="_blank" rel="noopener"><div class="pl">▶</div><span>${L('Find the trailer on YouTube', 'Trouver la bande-annonce sur YouTube')}</span></a>`;
    const facts = (d.facts || []).filter(f => f[1]);
    const el = document.createElement('div'); el.id = 'tov';
    el.innerHTML = `<div class="sheet" role="dialog" aria-modal="true" aria-label="${esc(d.t)}">
      <div class="grab"><span>${esc(d.kicker)}</span><button class="x" aria-label="${L('Close', 'Fermer')}">×</button></div>
      <div class="in">
        <div class="hero">${d.img ? `<img class="pst" src="${esc(d.img)}" alt="${esc(d.t)} poster" referrerpolicy="no-referrer">` : `<div class="pst ph">${esc(d.t)}</div>`}
          <div class="ht">${d.when ? `<p class="when">${esc(d.when)}</p>` : ''}<h2>${esc(d.t)}</h2>${d.meta ? `<p class="meta">${esc(d.meta)}</p>` : ''}${d.where ? `<p class="meta"><b>${L('Where', 'Où')}:</b> ${esc(d.where)}</p>` : ''}</div>
        </div>
        ${trailer}
        ${d.why ? `<h4>${L('Why you', 'Pourquoi toi')}</h4><p class="txt why">${esc(d.why)}</p>` : ''}
        <h4>${L('The story', 'L\'histoire')}</h4><div class="about">${d.about ? `<p class="txt">${esc(d.about)}</p>` : `<p class="loading">${L('Loading…', 'Chargement…')}</p>`}</div>
        <div class="fx">${facts.length ? `<ul class="facts">${facts.map(f => `<li><b>${esc(f[0])}</b><span>${esc(f[1])}</span></li>`).join('')}</ul>` : ''}</div>
        ${d.buttons ? `<div class="btns">${d.buttons}</div>` : ''}
        ${d.link ? `<a class="more" href="${esc(d.link)}" target="_blank" rel="noopener">${L('More ›', 'En savoir plus ›')}</a>` : ''}
      </div></div>`;
    document.body.appendChild(el); ov = el;
    const img = el.querySelector('img.pst'); if (img) img.onerror = () => { const ph = document.createElement('div'); ph.className = 'pst ph'; ph.textContent = d.t; img.replaceWith(ph); };
    requestAnimationFrame(() => requestAnimationFrame(() => el.classList.add('on')));
    el.querySelector('.x').onclick = close;
    el.addEventListener('click', e => { if (e.target === el) close(); });
    el.querySelectorAll('.btns button[data-a]').forEach(b => b.onclick = () => { const t = d.card && d.card.querySelector('.btns button[data-a="' + b.dataset.a + '"]'); close(); if (t) t.click(); });
    // swipe the sheet down from the top to close
    const sh = el.querySelector('.sheet'); let y0 = null, dy = 0;
    sh.addEventListener('touchstart', e => { y0 = sh.scrollTop <= 0 ? e.touches[0].clientY : null; dy = 0; }, { passive: true });
    sh.addEventListener('touchmove', e => { if (y0 == null) return; dy = e.touches[0].clientY - y0; if (dy > 0) { sh.style.transition = 'none'; sh.style.transform = 'translateY(' + dy + 'px)'; } }, { passive: true });
    sh.addEventListener('touchend', () => { if (y0 == null) return; sh.style.transition = ''; sh.style.transform = ''; if (dy > 110) close(); y0 = null; });
    // live synopsis when the paper did not print one
    if (!d.about) liveInfo(d.specs, d.t).then(v => {
      if (ov !== el) return;
      const a = el.querySelector('.about');
      if (!v || !v.text) { a.innerHTML = `<p class="txt" style="color:var(--muted)">${L('No synopsis yet. The trailer is the best preview for now.', 'Pas encore de synopsis. La bande-annonce reste le meilleur aperçu.')}</p>`; return; }
      a.innerHTML = `<p class="txt">${esc(v.text)}</p><p class="src">${L('Source', 'Source')}: ${v.link ? `<a href="${esc(v.link)}" target="_blank" rel="noopener" style="color:inherit">${esc(v.source)}</a>` : esc(v.source)}</p>`;
      if (!facts.length && v.facts && v.facts.length) el.querySelector('.fx').innerHTML = `<ul class="facts">${v.facts.map(f => `<li><b>${esc(f[0])}</b><span>${esc(f[1])}</span></li>`).join('')}</ul>`;
    });
  }

  // ---------- what was tapped ----------
  function fromPoster(fig) {
    const ds = fig.dataset, img = fig.querySelector('img.pp');
    const b = fig.querySelector('figcaption b');
    return { kicker: L('Coming soon', 'Bientôt'), t: ds.t || (fig.querySelector('figcaption') || {}).textContent || '',
      when: b ? b.textContent.trim() : '', meta: ds.meta || '', where: ds.where || '', about: ds.about || '', yt: ds.yt || '',
      img: img ? img.src : (ds.src || ''), specs: ds.pwiki || '', link: ds.link || '', y: ds.y || '' };
  }
  function fromPick(card) {
    let picks = []; try { picks = JSON.parse(card.dataset.pick); } catch (e) {}
    const h = card.querySelector('h4'); const t = h ? h.textContent : '';
    const p = picks.find(x => x.t === t); if (!p) return null;
    const img = card.querySelector('.pimg');
    const lab = [['seen', L('✓ Seen it', '✓ Déjà vu')], ['list', L('+ My list', '+ Ma liste'), 'add'], ['later', L('? Not sure', '? Pas sûr')], ['no', L('✗ Not for me', '✗ Pas pour moi')]];
    return { kicker: L("Tonight's pick", 'À voir ce soir'), t: p.t, y: p.y, meta: [p.kind, p.y, p.rt ? 'Rotten Tomatoes ' + p.rt : ''].filter(Boolean).join(' · '),
      where: p.where || '', why: p.why || '', about: p.about || '', yt: p.yt || p.trailer || '', img: img && !img.hidden && img.src ? img.src : (p.img || ''),
      specs: p.wiki || '', link: p.link || '', card, buttons: lab.map(x => `<button data-a="${x[0]}"${x[2] ? ' class="add"' : ''}>${x[1]}</button>`).join('') };
  }
  document.addEventListener('click', e => {
    if (ov && ov.contains(e.target)) return;
    const fig = e.target.closest && e.target.closest('.pgrid .poster');
    if (fig) { e.preventDefault(); open(fromPoster(fig)); return; }
    const pw = e.target.closest && e.target.closest('.pick .pwrap');
    if (pw) { const d = fromPick(pw.closest('.pick')); if (d) { e.preventDefault(); open(d); } }
  });
  document.addEventListener('keydown', e => { if (e.key === 'Escape') close(); });
})();
