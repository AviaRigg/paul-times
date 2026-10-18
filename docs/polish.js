/* The Paul Times: polish layer (motion). Loaded on every issue by index.html. */
(function () {
  const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
  const reader = document.getElementById('reader');
  if (!reader) return;
  if (!reduce) document.documentElement.classList.add('tpt-anim');

  // ---- swipe depth: neighbouring pages recede slightly ----
  let raf = 0;
  function depth() {
    raf = 0;
    const w = reader.clientWidth || 1, x = reader.scrollLeft / w;
    const lo = Math.floor(x) - 1, hi = Math.ceil(x) + 1;
    reader.querySelectorAll('.page.pz').forEach(p => { const i = +p.dataset.i; if (i < lo || i > hi) { p.classList.remove('pz'); p.style.removeProperty('--p'); p.style.removeProperty('--pa'); } });
    const pages = reader.children;
    for (let i = Math.max(0, lo); i <= Math.min(pages.length - 1, hi); i++) {
      const p = pages[i], d = Math.max(-1, Math.min(1, i - x));
      p.dataset.i = i;
      if (Math.abs(d) < .002) { p.classList.remove('pz'); continue; }
      p.classList.add('pz'); p.style.setProperty('--p', d.toFixed(4)); p.style.setProperty('--pa', Math.abs(d).toFixed(4));
    }
  }
  if (!reduce) reader.addEventListener('scroll', () => { if (!raf) raf = requestAnimationFrame(depth); }, { passive: true });

  // ---- reveal blocks as they come into view inside each page ----
  const seenPages = new WeakSet();
  let io = null;
  function setupReveal() {
    if (reduce) return;
    if (io) io.disconnect();
    const pages = [...reader.querySelectorAll('.page')];
    const w = reader.clientWidth || 1, cur = Math.round(reader.scrollLeft / w);
    pages.forEach((p, i) => {
      p.dataset.i = i;
      const pb = p.querySelector('.pb'); if (!pb) return;
      const obs = new IntersectionObserver(es => es.forEach(e => {
        if (!e.isIntersecting) return;
        const b = e.target; obs.unobserve(b);
        const delay = Math.min(6, b._rvq || 0) * 70;
        setTimeout(() => b.classList.remove('rv0'), delay);
      }), { root: pb, threshold: 0.08, rootMargin: '0px 0px -4% 0px' });
      let q = 0;
      const top0 = pb.getBoundingClientRect().top - pb.scrollTop, fold = pb.clientHeight * 0.92;
      [...pb.children].forEach(b => {
        if (!b.classList.contains('blk')) return;
        if (i === cur && seenPages.has(p)) return;
        // Whatever is on the first screen of a page stays visible, so a swipe never shows an empty page.
        if (b.getBoundingClientRect().top - top0 < fold) return;
        b.classList.add('rv0'); b._rvq = q++;
        if (i === cur) obs.observe(b); else b._obs = obs;
      });
      p._obs = obs;
    });
    arrive(cur, true);
  }
  // A page's blocks only start revealing once you land on it, so each swipe feels alive.
  let lastCur = -1;
  function arrive(i, force) {
    if (i === lastCur && !force) return;
    lastCur = i;
    const p = reader.children[i]; if (!p) return;
    if (!seenPages.has(p)) {
      seenPages.add(p);
      p.classList.add('fresh'); setTimeout(() => p.classList.remove('fresh'), 1200);
      const obs = p._obs; if (obs) p.querySelectorAll('.pb > .blk.rv0').forEach(b => obs.observe(b));
    }
    countUp(p);
  }
  let st = 0;
  reader.addEventListener('scroll', () => { clearTimeout(st); st = setTimeout(() => arrive(Math.round(reader.scrollLeft / (reader.clientWidth || 1))), 90); }, { passive: true });

  // ---- count up "Number of the day" style figures ----
  function countUp(p) {
    if (reduce) return;
    p.querySelectorAll('.fun .big:not([data-counted])').forEach(el => {
      el.dataset.counted = 1;
      const txt = el.textContent.trim(), m = txt.match(/^([^\d-]*)(-?[\d,]*\.?\d+)(.*)$/);
      if (!m) return;
      const raw = m[2].replace(/,/g, ''), target = parseFloat(raw); if (!isFinite(target)) return;
      const dec = (raw.split('.')[1] || '').length, comma = m[2].includes(',');
      const fmt = v => { let s = v.toFixed(dec); if (comma) { const [a, b] = s.split('.'); s = a.replace(/\B(?=(\d{3})+(?!\d))/g, ',') + (b ? '.' + b : ''); } return m[1] + s + m[3]; };
      const t0 = performance.now(), dur = 1100; el.classList.add('counting');
      const step = now => { const k = Math.min(1, (now - t0) / dur), e = 1 - Math.pow(1 - k, 4); el.textContent = fmt(target * e); if (k < 1) requestAnimationFrame(step); else { el.textContent = txt; el.classList.remove('counting'); } };
      el.textContent = fmt(0); requestAnimationFrame(step);
    });
  }

  // ---- sudoku: little pop when a number goes in ----
  document.addEventListener('click', e => {
    const b = e.target.closest('.sdk .pad button'); if (!b || reduce) return;
    const sdk = b.closest('.sdk'), sel = sdk && sdk.querySelector('.grid .c.sel');
    if (sel) { sel.classList.remove('pop'); void sel.offsetWidth; sel.classList.add('pop'); }
  }, true);

  // ---- settings: slide up and down like an iOS sheet ----
  const sheet = document.getElementById('settings');
  if (sheet && !reduce) {
    let closing = false;
    new MutationObserver(() => {
      if (!sheet.hidden && !sheet.classList.contains('open') && !closing) {
        requestAnimationFrame(() => requestAnimationFrame(() => sheet.classList.add('open')));
      } else if (sheet.hidden && sheet.classList.contains('open') && !closing) {
        closing = true; sheet.hidden = false; sheet.classList.remove('open');
        setTimeout(() => { sheet.hidden = true; closing = false; }, 480);
      }
    }).observe(sheet, { attributes: true, attributeFilter: ['hidden'] });
  }

  // ---- re-run whenever the paper lays itself out again (text size, theme, language) ----
  let lt = 0;
  new MutationObserver(() => { clearTimeout(lt); lt = setTimeout(() => { lastCur = -1; setupReveal(); depth(); }, 30); }).observe(reader, { childList: true });
  setupReveal();
})();
