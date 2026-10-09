/* ==========================================================================
   arch575.bradmachado.com — js/app.js
   Renders the slides (title, site, story intro, ten levels, story outro) from
   data/levels.json + data/story.json into the <template>s in index.html, and owns slide state and navigation.

   Modes (css/app.css):
     'slides'  >= 900 px: one slide visible at a time.
     'scroll'  <  900 px: slides stack; an IntersectionObserver sets the
               active slide as the page scrolls.

   Navigation: Left/Right, Up/Down (slides mode), Space (Shift+Space back),
   PageUp/PageDown, Home, End, F (fullscreen), I (replay the entry intro,
   js/intro.js: plays once on load at #01, any key or click skips it,
   prefers-reduced-motion shows its final frame), prev/next buttons, swipe
   (slides mode), URL hash #01..#nn (deep link and back button).

   Public API for js/tower.js (S5):
     window.deck.ready        Promise resolving to the parsed levels.json
     window.deck.data         parsed levels.json (after ready)
     window.deck.index        active slide index 0..count-1 (0 title, 1 site, then story/levels)
     window.deck.count        number of slides (12 without data/story.json)
     window.deck.slides[i]    { index, kind: 'title'|'site'|'text'|'image'|'level', level, levelIndex, el }
                              levelIndex is 0..9 for level slides, -1 otherwise
     window.deck.mode         'slides' | 'scroll'
     window.deck.on('change', (index, slide) => {})
                              fires on every slide change; if the deck is already
                              rendered the handler is also called at once with the
                              current slide. Returns an unsubscribe function.
     window.deck.go(i) / next() / prev()
   A 'deck:change' CustomEvent ({detail: {index, slide}}) is also dispatched on
   window. The tower canvas is <canvas id="tower"> inside #tower-wrap; its box
   changes size between slide kinds, so the renderer should watch #tower-wrap
   with a ResizeObserver.
   ========================================================================== */

const DATA_URL = 'data/levels.json';
const STORY_URL = 'data/story.json';  // optional story slides (review T4); absent = 12 slides
const PX_PER_IN = 96;          // CSS px per inch
const FT_PER_IN = 40;          // plan scale, 1 in = 40 ft
const SCALE_STEPS = [200, 100, 50, 20];

const pad2 = (n) => String(n).padStart(2, '0');

const mqSlides = window.matchMedia('(min-width: 900px)');
const mqReduced = window.matchMedia('(prefers-reduced-motion: reduce)');

const deckEl = document.getElementById('deck');
const towerWrap = document.getElementById('tower-wrap');
const countEl = document.getElementById('deck-count');
const prevBtn = document.getElementById('deck-prev');
const nextBtn = document.getElementById('deck-next');

const state = {
  index: -1,
  slides: [],
  data: null,
  ready: false,
  ignoreNextHash: false,
  observer: null,
};

const listeners = new Map();

function emit(name, ...args) {
  const set = listeners.get(name);
  if (!set) return;
  for (const fn of set) {
    try { fn(...args); } catch (err) { console.error(err); }
  }
}

let resolveReady;
const readyPromise = new Promise((res) => { resolveReady = res; });

const deck = {
  get index() { return state.index; },
  get count() { return state.slides.length; },
  get slides() { return state.slides; },
  get data() { return state.data; },
  get mode() { return mqSlides.matches ? 'slides' : 'scroll'; },
  ready: readyPromise,
  on(name, fn) {
    if (!listeners.has(name)) listeners.set(name, new Set());
    listeners.get(name).add(fn);
    if (name === 'change' && state.ready && state.index >= 0) {
      fn(state.index, state.slides[state.index]);
    }
    return () => deck.off(name, fn);
  },
  off(name, fn) { listeners.get(name)?.delete(fn); },
  go(i) { activate(i); },
  next() { activate(state.index + 1); },
  prev() { activate(state.index - 1); },
};
window.deck = deck;

/* --------------------------------------------------------------------------
   Rendering
   -------------------------------------------------------------------------- */

function clone(id) {
  return document.getElementById(id).content.firstElementChild.cloneNode(true);
}

function field(root, name) {
  return root.querySelector(`[data-f="${name}"]`);
}

function setText(root, name, text) {
  const el = field(root, name);
  if (el) el.textContent = text ?? '';
}

function setLines(root, name, lines) {
  const el = field(root, name);
  if (!el) return;
  el.replaceChildren(...lines.map((t) => {
    const p = document.createElement('p');
    p.textContent = t;
    return p;
  }));
}

function luminance(hex) {
  const m = /^#?([0-9a-f]{6})$/i.exec(hex.trim());
  if (!m) return 1;
  const n = parseInt(m[1], 16);
  const ch = (v) => {
    const c = v / 255;
    return c <= 0.03928 ? c / 12.92 : ((c + 0.055) / 1.055) ** 2.4;
  };
  return 0.2126 * ch(n >> 16) + 0.7152 * ch((n >> 8) & 255) + 0.0722 * ch(n & 255);
}

function renderTitle(t) {
  const el = clone('tpl-title');
  setText(el, 'eyebrow', t.eyebrow);
  setText(el, 'h1', t.h1);
  setLines(el, 'lines', t.lines);
  return el;
}

function renderSite(s) {
  const el = clone('tpl-site');
  setText(el, 'label', s.label);
  setText(el, 'name', s.name);
  setText(el, 'sub', s.sub);
  setLines(el, 'lines', s.lines);
  const img = field(el, 'img');
  img.alt = `${s.name}, ${s.sub}`;
  setText(el, 'caption', `Fig. 00 — ${s.name}, ${s.sub}.`);
  return el;
}

// Story slides (data/story.json): 'text' = title layout with a heading, lines and an
// optional ruled table, tower cols 7-12; 'image' = site layout; 'closing' = the title again.
function renderText(t) {
  const el = clone('tpl-text');
  setText(el, 'eyebrow', t.eyebrow);
  setText(el, 'heading', t.heading);
  setLines(el, 'lines', t.lines || []);
  const tbody = field(el, 'rows');
  for (const [k, v] of t.rows || []) {
    const tr = document.createElement('tr');
    const th = document.createElement('th');
    th.scope = 'row';
    th.textContent = k;
    const td = document.createElement('td');
    td.textContent = v;
    tr.append(th, td);
    tbody.append(tr);
  }
  if (!(t.rows || []).length) tbody.parentElement.remove();
  return el;
}

function renderImage(t) {
  const el = clone('tpl-site');
  el.classList.add('slide--image');
  setText(el, 'label', t.label);
  setText(el, 'name', t.name);
  setText(el, 'sub', t.sub);
  setLines(el, 'lines', t.lines || []);
  const img = field(el, 'img');
  img.src = t.src;
  img.alt = t.caption;
  setText(el, 'caption', `Fig. ${pad2(t.fig)} — ${t.caption}.`);
  return el;
}

function renderStory(t, data) {
  if (t.kind === 'text') return { kind: 'text', el: renderText(t) };
  if (t.kind === 'image') return { kind: 'image', el: renderImage(t) };
  if (t.kind === 'closing') return { kind: 'title', el: renderTitle(data.title) };
  return null;
}

function renderLevel(level, n, data) {
  const el = clone('tpl-level');
  setText(el, 'label', level.label);
  setText(el, 'name', level.name);
  setText(el, 'sub', level.sub);
  setText(el, 'description', level.description);

  // Ruled data table
  const tbody = field(el, 'rows');
  for (const [k, v] of level.rows) {
    const tr = document.createElement('tr');
    const th = document.createElement('th');
    th.scope = 'row';
    th.textContent = k;
    const td = document.createElement('td');
    td.textContent = v;
    tr.append(th, td);
    tbody.append(tr);
  }

  // Vertical key: the level program first (accent), then the rest in KEY_ORDER
  const programs = new Map(data.programs.map((p) => [p.key, p]));
  const keys = [level.program, ...level.keys.filter((k) => k !== level.program)];
  const ul = field(el, 'key');
  for (const k of keys) {
    const p = programs.get(k);
    if (!p) continue;
    const isAccent = k === level.program;
    const color = isAccent ? data.accent : p.color;
    const li = document.createElement('li');
    if (isAccent) li.className = 'key__item--accent';
    const sw = document.createElement('span');
    sw.className = 'key__swatch' + (!isAccent && luminance(color) >= 0.6 ? ' key__swatch--bordered' : '');
    sw.style.background = color;
    const lb = document.createElement('span');
    lb.className = 'key__label';
    lb.textContent = p.label;
    li.append(sw, lb);
    ul.append(li);
  }

  // Plan, scale bar, caption
  const img = field(el, 'plan');
  img.src = level.plan;
  img.alt = `Plan, ${level.label} ${level.name}`;
  img.decoding = 'async';
  setText(el, 'caption', `Fig. ${pad2(n)} — ${level.name}, 1 in = ${FT_PER_IN} ft.`);
  return el;
}

/* Fit the plan into its column (slides mode) so the scale bar and caption sit
   directly under the rendered image, then size the scale bar from the fit.
   The SVG plan is drawn at 1 in = 40 ft, so 1 ft = 96/40 px before fitting. */
function updateScale(fig) {
  const img = fig.querySelector('.plan__img');
  const svg = fig.querySelector('.plan__scale');
  const cap = fig.querySelector('figcaption');
  if (!img || !svg || !img.naturalWidth || !img.naturalHeight) return;

  let s;
  if (deck.mode === 'slides') {
    const figW = fig.clientWidth;
    const figH = fig.clientHeight;
    const outer = (el) => {
      const cs = getComputedStyle(el);
      return el.getBoundingClientRect().height + parseFloat(cs.marginTop) + parseFloat(cs.marginBottom);
    };
    const avail = figH - outer(svg) - outer(cap);
    if (figW <= 0 || avail <= 0) return;
    s = Math.min(figW / img.naturalWidth, avail / img.naturalHeight);
    img.style.height = `${Math.floor(img.naturalHeight * s)}px`;
  } else {
    img.style.height = '';
    const r = img.getBoundingClientRect();
    if (!r.width || !r.height) return;
    s = Math.min(r.width / img.naturalWidth, r.height / img.naturalHeight);
  }

  const boxW = img.getBoundingClientRect().width;
  const pxPerFt = s * PX_PER_IN / FT_PER_IN;
  const maxPx = boxW * 0.45;
  const ft = SCALE_STEPS.find((f) => f * pxPerFt <= maxPx) ?? SCALE_STEPS[SCALE_STEPS.length - 1];
  const L = Math.round(ft * pxPerFt);
  const y = 16;
  const nx = L + 92;              // clears the 13 px "200 ft" label
  const w = Math.max(boxW, nx + 40);
  svg.setAttribute('viewBox', `0 0 ${w} 24`);
  svg.setAttribute('width', String(w));
  svg.innerHTML =
    `<path class="sb" d="M0.5,${y - 6} V${y}.5 H${L + 0.5} V${y - 6}"/>` +
    `<text x="${L + 8}" y="${y + 1}">${ft} ft</text>` +
    `<path class="sb-fill" d="M${nx},${y - 4} L${nx + 10},${y - 8} V${y} Z"/>` +
    `<path class="sb" d="M${nx + 10},${y - 4}.5 H${nx + 28}"/>` +
    `<text x="${nx + 36}" y="${y + 1}">N</text>`;
}

function updateScales() {
  for (const fig of deckEl.querySelectorAll('.slide--level .plan')) updateScale(fig);
}

function build(data) {
  const frag = document.createDocumentFragment();
  const slides = [];

  const titleEl = renderTitle(data.title);
  slides.push({ index: 0, kind: 'title', level: null, levelIndex: -1, el: titleEl });
  frag.append(titleEl);

  const siteEl = renderSite(data.site);
  slides.push({ index: 1, kind: 'site', level: null, levelIndex: -1, el: siteEl });
  frag.append(siteEl);

  const story = data.story || { intro: [], outro: [] };
  for (const t of story.intro || []) {
    const r = renderStory(t, data);
    if (!r) continue;
    slides.push({ index: slides.length, kind: r.kind, level: null, levelIndex: -1, el: r.el });
    frag.append(r.el);
  }

  // Title and site go before the tower wrapper (phone: tower sticks from here down)
  deckEl.insertBefore(frag, towerWrap);

  data.levels.forEach((level, k) => {
    const el = renderLevel(level, k + 1, data);
    slides.push({ index: slides.length, kind: 'level', level, levelIndex: k, el });
    deckEl.append(el);
  });

  for (const t of story.outro || []) {
    const r = renderStory(t, data);
    if (!r) continue;
    r.el.classList.add('slide--outro');
    slides.push({ index: slides.length, kind: r.kind, level: null, levelIndex: -1, el: r.el });
    deckEl.append(r.el);
  }

  slides.forEach((s) => {
    s.el.id = `s${pad2(s.index + 1)}`;
    s.el.dataset.index = String(s.index);
    s.el.setAttribute('aria-label', `Slide ${pad2(s.index + 1)} of ${pad2(slides.length)}`);
  });

  state.slides = slides;
  state.data = data;

  // Scale bars follow the rendered plan size
  const ro = new ResizeObserver((entries) => {
    for (const e of entries) updateScale(e.target);
  });
  deckEl.querySelectorAll('.slide--level .plan').forEach((fig) => {
    ro.observe(fig);
    fig.querySelector('.plan__img').addEventListener('load', () => updateScale(fig));
  });
}

/* --------------------------------------------------------------------------
   State
   -------------------------------------------------------------------------- */

function hashIndex() {
  const m = /^#(\d{2})$/.exec(location.hash);
  if (!m) return -1;
  const i = Number(m[1]) - 1;
  return i >= 0 && i < state.slides.length ? i : -1;
}

function writeHash(i, replace) {
  const h = `#${pad2(i + 1)}`;
  if (location.hash === h) return;
  if (replace) {
    history.replaceState(null, '', h);
  } else {
    state.ignoreNextHash = true;
    location.hash = h;
  }
}

function activate(i, { fromHash = false, fromScroll = false, replace = false, instant = false } = {}) {
  const n = state.slides.length;
  if (!n) return;
  i = Math.max(0, Math.min(n - 1, i));
  const changed = i !== state.index;
  state.index = i;
  const slide = state.slides[i];

  state.slides.forEach((s, k) => s.el.classList.toggle('is-active', k === i));
  deckEl.dataset.kind = slide.kind;
  countEl.textContent = `${pad2(i + 1)} / ${pad2(n)}`;
  prevBtn.disabled = i === 0;
  nextBtn.disabled = i === n - 1;

  if (!fromHash) writeHash(i, replace || fromScroll);

  if (deck.mode === 'scroll' && !fromScroll) {
    const behavior = instant || mqReduced.matches ? 'instant' : 'smooth';
    if (i === 0) window.scrollTo({ top: 0, behavior });            // keep the header in view
    else slide.el.scrollIntoView({ behavior, block: 'start' });
  }

  requestAnimationFrame(updateScales);

  if (changed) {
    emit('change', i, slide);
    window.dispatchEvent(new CustomEvent('deck:change', { detail: { index: i, slide } }));
  }
}

/* --------------------------------------------------------------------------
   Input
   -------------------------------------------------------------------------- */

function toggleFullscreen() {
  if (document.fullscreenElement) {
    document.exitFullscreen?.();
  } else {
    document.documentElement.requestFullscreen?.()?.catch?.(() => {});
  }
}

window.addEventListener('keydown', (e) => {
  if (e.altKey || e.ctrlKey || e.metaKey) return;
  if (window.intro?.state === 'playing') return;   // S15: the first key only skips the intro (js/intro.js)
  const t = e.target;
  if (t && /^(INPUT|TEXTAREA|SELECT)$/.test(t.tagName)) return;
  const slides = deck.mode === 'slides';
  switch (e.key) {
    case 'ArrowRight':
    case 'PageDown':
      e.preventDefault(); deck.next(); break;
    case 'ArrowLeft':
    case 'PageUp':
    case 'Backspace':
      e.preventDefault(); deck.prev(); break;
    case ' ':
    case 'Spacebar':
      e.preventDefault(); if (e.shiftKey) deck.prev(); else deck.next(); break;
    case 'ArrowDown':
      if (slides) { e.preventDefault(); deck.next(); } break;
    case 'ArrowUp':
      if (slides) { e.preventDefault(); deck.prev(); } break;
    case 'Home':
      e.preventDefault(); deck.go(0); break;
    case 'End':
      e.preventDefault(); deck.go(state.slides.length - 1); break;
    case 'f':
    case 'F':
      toggleFullscreen(); break;
    case 'i':
    case 'I':
      window.intro?.replay(); break;      // S15: replay the entry intro (js/intro.js) from #01
    default:
      break;
  }
});

prevBtn.addEventListener('click', () => deck.prev());
nextBtn.addEventListener('click', () => deck.next());

// Swipe (slides mode only; in scroll mode the page scrolls natively)
let touchStart = null;
deckEl.addEventListener('touchstart', (e) => {
  if (e.touches.length !== 1) { touchStart = null; return; }
  touchStart = { x: e.touches[0].clientX, y: e.touches[0].clientY };
}, { passive: true });
deckEl.addEventListener('touchend', (e) => {
  if (!touchStart || deck.mode !== 'slides') { touchStart = null; return; }
  const dx = e.changedTouches[0].clientX - touchStart.x;
  const dy = e.changedTouches[0].clientY - touchStart.y;
  touchStart = null;
  if (Math.abs(dx) > 60 && Math.abs(dx) > Math.abs(dy) * 1.5) {
    if (dx < 0) deck.next(); else deck.prev();
  }
}, { passive: true });

window.addEventListener('hashchange', () => {
  if (state.ignoreNextHash) { state.ignoreNextHash = false; return; }
  const i = hashIndex();
  if (i >= 0) activate(i, { fromHash: true });
});

/* Scroll mode: a 1vh band just below the sticky tower (40vh) decides the
   active slide; the band sits at 40vh so the title and site slides, which
   scroll above the tower, are picked up at the same reading line. */
function startObserver() {
  stopObserver();
  state.observer = new IntersectionObserver((entries) => {
    for (const en of entries) {
      if (!en.isIntersecting) continue;
      const i = Number(en.target.dataset.index);
      if (i !== state.index) activate(i, { fromScroll: true });
    }
  }, { root: document, rootMargin: '-40% 0px -59% 0px', threshold: 0 });   // root: document = this viewport, also when iframed
  state.slides.forEach((s) => state.observer.observe(s.el));
}

function stopObserver() {
  state.observer?.disconnect();
  state.observer = null;
}

function applyMode() {
  if (deck.mode === 'scroll') {
    startObserver();
  } else {
    stopObserver();
    window.scrollTo(0, 0);
  }
  requestAnimationFrame(updateScales);
}

mqSlides.addEventListener('change', applyMode);
window.addEventListener('resize', () => requestAnimationFrame(updateScales));

// Scroll mode: plans load after the first deep-link jump and grow the page,
// so re-align the target slide once everything has loaded.
window.addEventListener('load', () => {
  if (deck.mode !== 'scroll' || !state.ready) return;
  const i = hashIndex();
  if (i > 0) activate(i, { fromHash: true, instant: true });
});

/* --------------------------------------------------------------------------
   Boot
   -------------------------------------------------------------------------- */

Promise.all([
  fetch(DATA_URL).then((r) => {
    if (!r.ok) throw new Error(`${DATA_URL}: HTTP ${r.status}`);
    return r.json();
  }),
  fetch(STORY_URL).then((r) => (r.ok ? r.json() : null)).catch(() => null),
])
  .then(([data, story]) => {
    if (story) data.story = story;
    build(data);
    const start = hashIndex();
    activate(start >= 0 ? start : 0, { replace: true, fromHash: start >= 0, instant: true });
    state.ready = true;
    applyMode();
    resolveReady(data);
  })
  .catch((err) => {
    console.error(err);
    countEl.textContent = '—';
  });
