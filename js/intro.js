/* ==========================================================================
   arch575.bradmachado.com — js/intro.js   (intro_v1.0, S15)
   This section is intended to play the entry sequence on slide 01: the city
   map zooms to Chicago scale, the map greys out while the Randolph corridor
   draws in the accent, the view zooms to the corridor, the map cross-fades to
   a top-down three.js view of the site model at the same framing, the camera
   descends to the S5 title camera with the tower standing on the site, and
   the title text fades in.

   Stages (plan §1 "Intro timing", ms):
     A  2500  city SVG, whole sheet -> city boundary filling the map height
     hA 1000  hold
     B  1000  #rest -> 0.3, #corridor draws (stroke-dashoffset), #sitebox in ink
     C  2500  zoom until Randolph (Michigan Ave -> site box) fills the width,
              city SVG cross-fades to the corridor SVG; caption at the end
     hC 1500  hold
     D1  800  map fades out, canvas fades in (top-down, same framing)
     D2 3000  yaw / pitch / distance / target tween to the title camera
     T   500  title text
   Total 12.8 s. requestAnimationFrame, ease-in-out-cubic on the motion stages.

   Both SVGs share one map frame (data/site.json mapFrame), so a view is
   {cx, cy, mpp} = centre in map metres and map metres per CSS pixel; each
   SVG gets its own matrix on g#map from its viewBox fit.

   Hooks: plays once on load at #01 (not on deep links); any key or click
   skips to the final frame; I replays; prefers-reduced-motion -> final frame;
   below 900 px only A-C play in a 40vh band at the top. Captures / checks:
   ?introat=A|B|C|cut|D|title freezes the end state of that stage (no
   animation; 'cut' also sets the map to 50 % over the canvas and writes the
   #sitebox vs 3D-extent measurement to #intro[data-measure]); the stage log
   is written to #intro[data-log] when the sequence ends.

   window.intro: .state 'idle'|'playing'|'done'|'skipped', .log, .replay(),
   .skip(), .measure()
   ========================================================================== */

const CITY_URL = 'assets/map-city.svg';
const CORR_URL = 'assets/map-corridor.svg';
const SITE_URL = 'data/site.json';
const ASSET_TIMEOUT_MS = 3000;       // if the maps are not in by then, the title shows instead
const FIT_PAD = 0.06;                // 6 % of the frame on each side
const START_OUT = 1.5;               // stage A starts this many times wider than Chicago scale
const FOV = 28;                      // deg, vertical, over the tower's grid box (tower.js)
const TOP_PITCH = -89.97;            // straight down, short of the look-at singularity
const DEG = Math.PI / 180;

const STAGES = [
  ['A', 2500], ['hA', 1000], ['B', 1000], ['C', 2500], ['hC', 1500],
  ['D1', 800], ['D2', 3000], ['T', 500],
];

const mqSlides = window.matchMedia('(min-width: 900px)');
const mqReduced = window.matchMedia('(prefers-reduced-motion: reduce)');
const params = new URLSearchParams(location.search);
const seekTo = params.get('introat');

const easeInOutCubic = (t) => (t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2);
const clamp01 = (t) => Math.min(1, Math.max(0, t));
const smooth = (t, a, b) => easeInOutCubic(clamp01((t - a) / (b - a)));

const wrap = document.getElementById('tower-wrap');

/* --------------------------------------------------------------------------
   Overlay
   -------------------------------------------------------------------------- */

const overlay = document.createElement('div');
overlay.id = 'intro';
overlay.hidden = true;
overlay.setAttribute('aria-hidden', 'true');
overlay.innerHTML =
  '<div class="intro__maps"></div>' +
  '<div class="intro__meta"><p class="intro__caption"></p><p class="intro__attribution"></p></div>';
document.body.append(overlay);
const mapsEl = overlay.querySelector('.intro__maps');
const captionEl = overlay.querySelector('.intro__caption');
const attributionEl = overlay.querySelector('.intro__attribution');

const st = {
  state: 'idle',
  t0: 0,
  stage: -1,
  log: [],
  raf: 0,
  phone: false,
  assets: null,         // { city, corr, site } once loaded
  views: null,          // { whole, city, corr }
  descent: null,        // { from, to } camera views for D2
  played: false,
};

const intro = {
  get state() { return st.state; },
  get log() { return st.log.slice(); },
  get views() { return st.views; },
  replay,
  skip,
  measure,
};
window.intro = intro;

/* --------------------------------------------------------------------------
   Assets
   -------------------------------------------------------------------------- */

function withTimeout(promise, ms, what) {
  return Promise.race([
    promise,
    new Promise((_, rej) => setTimeout(() => rej(new Error(`${what} not ready in ${ms} ms`)), ms)),
  ]);
}

async function fetchSvg(url) {
  const r = await fetch(url);
  if (!r.ok) throw new Error(`${url}: HTTP ${r.status}`);
  const doc = new DOMParser().parseFromString(await r.text(), 'image/svg+xml');
  const svg = doc.documentElement;
  if (svg.nodeName !== 'svg') throw new Error(`${url}: not an SVG`);
  const el = document.importNode(svg, true);
  el.removeAttribute('width');
  el.removeAttribute('height');
  el.setAttribute('preserveAspectRatio', 'xMidYMid meet');
  el.setAttribute('focusable', 'false');
  return el;
}

async function loadAssets() {
  if (st.assets) return st.assets;
  const [city, corr, site] = await Promise.all([
    fetchSvg(CITY_URL),
    fetchSvg(CORR_URL),
    fetch(SITE_URL).then((r) => { if (!r.ok) throw new Error(`${SITE_URL}: HTTP ${r.status}`); return r.json(); }),
  ]);
  city.classList.add('intro__svg', 'intro__svg--city');
  corr.classList.add('intro__svg', 'intro__svg--corridor');
  mapsEl.replaceChildren(city, corr);
  attributionEl.textContent = site.attribution || 'Map data © OpenStreetMap contributors';
  const miles = site.randolph?.toSiteCentreMiles ?? site.corridorMiles;
  captionEl.textContent = `Randolph St · Michigan Ave → 725 W Randolph · ${miles.toFixed(1)} mi`;
  st.assets = { city, corr, site };
  return st.assets;
}

/* --------------------------------------------------------------------------
   Map frame <-> model <-> scene
   -------------------------------------------------------------------------- */

// data/site.json transform.modelFtToMap is a 2x3 affine: map = A m + b
function modelFtToMap(site, X, Y) {
  const [[a, b, tx], [c, d, ty]] = site.transform.modelFtToMap;
  return [a * X + b * Y + tx, c * X + d * Y + ty];
}

function mapToModelFt(site, mx, my) {
  const [[a, b, tx], [c, d, ty]] = site.transform.modelFtToMap;
  const det = a * d - b * c;
  const x = mx - tx, y = my - ty;
  return [(d * x - b * y) / det, (-c * x + a * y) / det];
}

/* --------------------------------------------------------------------------
   Views: {cx, cy, mpp} in the shared map frame
   -------------------------------------------------------------------------- */

function frameSize() {
  const r = mapsEl.getBoundingClientRect();
  return { W: r.width, H: r.height, left: r.left, top: r.top };
}

function fitInfo(svg) {
  const vb = svg.viewBox.baseVal;
  const { W, H } = frameSize();
  const s0 = Math.min(W / vb.width, H / vb.height);          // px per user unit at identity
  return { s0, vcx: vb.x + vb.width / 2, vcy: vb.y + vb.height / 2 };
}

function applyView(svg, view) {
  const map = svg.querySelector('#map');
  const { s0, vcx, vcy } = fitInfo(svg);
  const k = 1 / (view.mpp * s0);
  map.setAttribute('transform', `matrix(${k} 0 0 ${k} ${vcx - k * view.cx} ${vcy - k * view.cy})`);
}

function bboxOf(svg, ids) {
  let x0 = Infinity, y0 = Infinity, x1 = -Infinity, y1 = -Infinity;
  for (const id of ids) {
    const el = svg.querySelector(`#${id}`);
    if (!el) continue;
    const b = el.getBBox();
    x0 = Math.min(x0, b.x); y0 = Math.min(y0, b.y);
    x1 = Math.max(x1, b.x + b.width); y1 = Math.max(y1, b.y + b.height);
  }
  return { x: x0, y: y0, width: x1 - x0, height: y1 - y0 };
}

function computeViews() {
  const { city, corr } = st.assets;
  const { W, H } = frameSize();
  const lim = 1 - 2 * FIT_PAD;
  city.querySelector('#map').removeAttribute('transform');
  corr.querySelector('#map').removeAttribute('transform');
  const cb = bboxOf(city, ['city-boundary']);
  const cityV = {
    cx: cb.x + cb.width / 2,
    cy: cb.y + cb.height / 2,
    mpp: Math.max(cb.height / (lim * H), cb.width / (lim * W)),   // boundary fills the height
  };
  // The city sheet's viewBox is already the city bbox (S13), so "whole sheet" starts
  // START_OUT x wider than Chicago scale and the sheet fades in during the approach
  const whole = { cx: cityV.cx, cy: cityV.cy, mpp: cityV.mpp * START_OUT };
  const rb = bboxOf(corr, ['randolph', 'site-extent']);
  const corrV = {
    cx: rb.x + rb.width / 2,
    cy: rb.y + rb.height / 2,
    mpp: Math.max(rb.width / (lim * W), rb.height / (lim * H)),   // Michigan Ave -> site box fills the width
  };
  st.views = { whole, city: cityV, corr: corrV };
  return st.views;
}

// Zoom between two views: scale exponential, centre so the destination stays put
function lerpView(a, b, e) {
  const r = b.mpp / a.mpp;
  const mpp = a.mpp * Math.pow(r, e);
  const u = Math.abs(1 - r) < 1e-9 ? e : (1 - Math.pow(r, e)) / (1 - r);
  return { cx: a.cx + (b.cx - a.cx) * u, cy: a.cy + (b.cy - a.cy) * u, mpp };
}

/* --------------------------------------------------------------------------
   Stage states
   -------------------------------------------------------------------------- */

function setGreyOut(e) {
  for (const svg of [st.assets.city, st.assets.corr]) {
    svg.querySelector('#rest').style.opacity = String(1 - 0.7 * e);
    const r = svg.querySelector('#randolph');
    r.style.strokeDasharray = '1000';
    r.style.strokeDashoffset = String(1000 * (1 - e));
    svg.querySelector('#sitebox').style.opacity = String(e);
  }
}

function setMaps(view, corrMix, cityOpacity = 1 - corrMix) {
  const { city, corr } = st.assets;
  // a fully transparent sheet is not painted at all (both sheets repaint every frame)
  city.style.visibility = cityOpacity > 0 ? '' : 'hidden';
  corr.style.visibility = corrMix > 0 ? '' : 'hidden';
  if (cityOpacity > 0) applyView(city, view);
  if (corrMix > 0) applyView(corr, view);
  city.style.opacity = String(cityOpacity);
  corr.style.opacity = String(corrMix);
}

function setTitleText(k) {
  const text = document.querySelector('.slide--title.is-active .slide__text') || document.querySelector('.slide--title .slide__text');
  if (!text) return;
  text.style.opacity = k == null ? '' : String(k);
}

// Camera at the cut: straight down over the map frame, same scale as the corridor view
function computeDescent() {
  const tower = window.tower;
  const { site } = st.assets;
  const v = st.views.corr;
  if (!tower || tower.status === 'fallback' || !tower.modelFtToScene(0, 0, 0) || !tower.titleView()) return null;
  const box = tower.box || wrap.getBoundingClientRect();
  const f = frameSize();
  const g = site.towerPlacement?.groundFt ?? 0;
  // ground point under the projection's principal point (the grid box centre)
  const pcx = box.left + box.width / 2, pcy = box.top + box.height / 2;
  const mx = v.cx + (pcx - (f.left + f.W / 2)) * v.mpp;
  const my = v.cy + (pcy - (f.top + f.H / 2)) * v.mpp;
  const [X, Y] = mapToModelFt(site, mx, my);
  const ground = tower.modelFtToScene(X, Y, g);
  // map north and the map -> scene metre ratio from two frame points 1000 m apart
  const [Xn, Yn] = mapToModelFt(site, mx, my - 1000);
  const north = tower.modelFtToScene(Xn, Yn, g).sub(ground);
  const ratio = Math.hypot(north.x, north.z) / 1000;      // scene m per map m (0.7445: Mercator -> ground)
  north.normalize();
  const yaw = Math.atan2(-north.x, -north.z) / DEG;        // screen-up = -(sin az, cos az)
  const h = v.mpp * ratio * box.height / (2 * Math.tan(FOV / 2 * DEG));
  const eps = h * Math.cos(TOP_PITCH * DEG);               // the camera sits exactly above `ground`
  const from = {
    yawDeg: yaw,
    pitchDeg: TOP_PITCH,
    distance: h,
    target: [ground.x - eps * Math.sin(yaw * DEG), ground.y, ground.z - eps * Math.cos(yaw * DEG)],
  };
  const to = tower.titleView();
  let dYaw = (((to.yawDeg - from.yawDeg) % 360) + 540) % 360 - 180;
  return { from, to, dYaw, ratio, altitude: h };
}

function setDescent(e) {
  const d = st.descent;
  if (!d) return;
  const { from, to } = d;
  window.tower.setCamera({
    yawDeg: from.yawDeg + d.dYaw * e,
    pitchDeg: from.pitchDeg + (to.pitchDeg - from.pitchDeg) * e,
    distance: from.distance * Math.pow(to.distance / from.distance, e),
    target: from.target.map((a, i) => a + (to.target[i] - a) * e),
  });
}

// Visual state at the start of the sequence
function reset() {
  const { city, corr } = st.assets;
  overlay.hidden = false;
  overlay.style.opacity = '1';
  computeViews();
  setMaps(st.views.whole, 0, 0);
  setGreyOut(0);
  captionEl.style.opacity = '0';
  if (!st.phone) {
    document.body.classList.add('is-intro');
    setTitleText(0);
    window.tower?.setFull(true);
    wrap.style.opacity = '0';
  }
}

// Apply stage `id` at progress e (0..1)
function apply(id, e) {
  const V = st.views;
  switch (id) {
    case 'A': setMaps(lerpView(V.whole, V.city, easeInOutCubic(e)), 0, Math.min(1, e / 0.3)); break;
    case 'hA': break;                                            // set on enter; no repaint while holding
    case 'B': setGreyOut(easeInOutCubic(e)); break;
    case 'C':
      setMaps(lerpView(V.city, V.corr, easeInOutCubic(e)), smooth(e, 0.3, 0.75));
      captionEl.style.opacity = String(smooth(e, 0.8, 1));
      break;
    case 'hC': break;                                            // set on enter
    case 'D1':
      overlay.style.opacity = String(1 - e);
      if (!st.phone) { wrap.style.opacity = String(e); setDescent(0); }
      break;
    case 'D2': setDescent(easeInOutCubic(e)); break;
    case 'T': setTitleText(e); break;
    default: break;
  }
}

// Entering a stage: one-off state for it
function enter(id) {
  if (id === 'hA' || id === 'B') setMaps(st.views.city, 0);
  if (id === 'hC') { setMaps(st.views.corr, 1); setGreyOut(1); captionEl.style.opacity = '1'; }
  if (id === 'D1' && !st.phone) {
    st.descent = computeDescent();
    window.tower?.setContext(true, 0);         // whatever is loaded shows at once at the cut
    setDescent(0);
  }
  if (id === 'D2' && !st.phone) setDescent(0);
  if (id === 'T') {
    overlay.hidden = true;
    if (!st.phone) { window.tower?.setCamera(null); wrap.style.opacity = ''; }
  }
}

/* --------------------------------------------------------------------------
   Sequence
   -------------------------------------------------------------------------- */

function sequence() {
  const ids = st.phone ? ['A', 'hA', 'B', 'C', 'hC', 'D1'] : STAGES.map((s) => s[0]);
  let at = 0;
  return ids.map((id) => {
    const ms = STAGES.find((s) => s[0] === id)[1];
    const s = { id, ms, start: at };
    at += ms;
    return s;
  });
}

function tick(now) {
  st.raf = 0;
  if (st.state !== 'playing') return;
  const t = now - st.t0;
  const seq = st.seq;
  let idx = seq.findIndex((s) => t < s.start + s.ms);
  if (idx < 0) { finish('done'); return; }
  while (st.stage < idx) {                       // enter every stage in order (frame drops)
    st.stage += 1;
    const s = seq[st.stage];
    st.log.push({ stage: s.id, at: Math.round(performance.now() - st.t0), frames: 0 });
    enter(s.id);
    if (st.stage < idx) apply(s.id, 1);
  }
  const s = seq[idx];
  apply(s.id, clamp01((t - s.start) / s.ms));
  st.log[st.log.length - 1].frames += 1;
  st.raf = requestAnimationFrame(tick);
}

function play() {
  st.phone = !mqSlides.matches;
  st.seq = sequence();
  st.stage = -1;
  st.log = [];
  st.descent = null;
  st.state = 'playing';
  st.played = true;
  reset();
  st.t0 = performance.now();
  st.log.push({ stage: 'start', at: 0 });
  st.raf = requestAnimationFrame(tick);
}

// Final frame: overlay gone, canvas full on #01 with the context, title camera, title text
function finalFrame() {
  if (st.raf) cancelAnimationFrame(st.raf);
  st.raf = 0;
  overlay.hidden = true;
  overlay.style.opacity = '';
  captionEl.style.opacity = '';
  document.body.classList.remove('is-intro');
  setTitleText(null);
  wrap.style.opacity = '';
  const tower = window.tower;
  if (tower) {
    tower.setCamera(null);
    if (window.deck?.index === 0) {
      tower.setFull(mqSlides.matches);
      tower.setContext(true);
    }
  }
}

function finish(state) {
  st.log.push({ stage: 'end', at: Math.round(performance.now() - st.t0) });
  st.state = state;
  finalFrame();
  overlay.dataset.log = JSON.stringify(st.log);
}

function skip() {
  if (st.state !== 'playing') return;
  finish('skipped');
}

function replay() {
  if (st.state === 'playing') return;
  if (!st.assets) return;
  if (window.deck && window.deck.index !== 0) window.deck.go(0);
  if (mqReduced.matches) { finalFrame(); return; }
  play();
}

/* --------------------------------------------------------------------------
   Checks: #sitebox (SVG) vs the 3D site-model extent at the cut
   -------------------------------------------------------------------------- */

function measure() {
  const tower = window.tower;
  const { site, corr } = st.assets || {};
  if (!site || !tower || !tower.modelFtToScene(0, 0, 0)) return null;
  const { min, max } = site.siteModelExtentFt;
  const g = site.towerPlacement?.groundFt ?? 0;
  const corners = [[min[0], min[1]], [max[0], min[1]], [max[0], max[1]], [min[0], max[1]]];
  const path = corr.querySelector('#site-extent');
  const ctm = path.getScreenCTM();
  const pt = corr.createSVGPoint();
  const W = window.innerWidth;
  const rows = corners.map(([X, Y]) => {
    const [mx, my] = modelFtToMap(site, X, Y);
    pt.x = mx; pt.y = my;
    const s = pt.matrixTransform(ctm);
    const p = tower.project(tower.modelFtToScene(X, Y, g));
    const d = Math.hypot(p.x - s.x, p.y - s.y);
    return { modelFt: [X, Y], svgPx: [+s.x.toFixed(1), +s.y.toFixed(1)], scenePx: [+p.x.toFixed(1), +p.y.toFixed(1)], dPx: +d.toFixed(2) };
  });
  const maxPx = Math.max(...rows.map((r) => r.dPx));
  // the context group's own bounds (visible geometry) against the transformed GLB extent from site.json
  const cb = tower.contextBounds?.();
  const ge = site.siteGlb?.extentFt;
  const glbExtentScene = ge ? [tower.modelFtToScene(ge[0][0], ge[0][1], ge[0][2]).toArray(), tower.modelFtToScene(ge[1][0], ge[1][1], ge[1][2]).toArray()] : null;
  const cbPx = cb && tower.vec3 ? [tower.project(tower.vec3(cb.min[0], 0, cb.min[2])), tower.project(tower.vec3(cb.max[0], 0, cb.max[2]))] : null;
  return { viewportW: W, maxPx, pctOfWidth: +((100 * maxPx) / W).toFixed(3), corners: rows, contextBounds: cb, glbExtentScene, contextBoundsPx: cbPx, descent: st.descent };
}

/* --------------------------------------------------------------------------
   Seek (captures): freeze the end state of a stage
   -------------------------------------------------------------------------- */

async function seek(id) {
  st.phone = !mqSlides.matches;
  st.seq = sequence();
  st.state = 'playing';
  reset();
  const order = ['A', 'hA', 'B', 'C', 'hC', 'D1', 'D2', 'T'];
  const upto = { A: 'A', B: 'B', C: 'hC', cut: 'D1', D: 'D2', title: 'T' }[id] || 'A';
  if (upto === 'D1' || upto === 'D2' || upto === 'T') {
    // the cut needs the GLBs in the scene for a meaningful capture
    await window.tower?.ready;
    await window.tower?.contextReady;
  }
  for (const s of order) {
    enter(s);
    if (s === 'D1' && upto === 'D1') { apply('D1', 1); overlay.style.opacity = params.get('overlay') ?? '0.5'; break; }
    apply(s, 1);
    if (s === upto) break;
  }
  st.stage = order.indexOf(upto);
  if (upto === 'T') finish('done');
  else st.state = 'done';
  if (!st.phone) {
    await window.tower?.ready;
    window.tower?.renderNow?.();                 // headless captures: no animation frame needed
  }
  if (upto === 'D1') overlay.dataset.measure = JSON.stringify(measure());
  overlay.dataset.seek = id;
  if (params.has('debug')) {
    const b = window.tower?.box, m = upto === 'D1' ? JSON.parse(overlay.dataset.measure) : null;
    captionEl.textContent += ` · vp ${window.innerWidth}×${window.innerHeight} · box ${b ? `${b.left},${b.top} ${b.width}×${b.height}` : '—'}` +
      (m ? ` · max ${m.maxPx} px = ${m.pctOfWidth} % · ctx px ${m.contextBoundsPx.map((p) => `${p.x.toFixed(0)},${p.y.toFixed(0)}`).join(' – ')}` : '');
  }
}

/* --------------------------------------------------------------------------
   Input and boot
   -------------------------------------------------------------------------- */

window.addEventListener('keydown', (e) => {
  if (st.state !== 'playing') return;
  if (e.ctrlKey || e.altKey || e.metaKey) return;
  if (/^(Shift|Control|Alt|Meta|CapsLock|Tab|F\d+)$/.test(e.key)) return;
  e.stopImmediatePropagation();                // the first key only skips; it does not navigate
  skip();
}, { capture: true });

window.addEventListener('click', (e) => {
  if (st.state !== 'playing') return;
  e.stopImmediatePropagation();
  e.preventDefault();
  skip();
}, { capture: true });

// Viewport change while the sequence is up: refit the map views and the descent frame
let resizeTimer = 0;
window.addEventListener('resize', () => {
  if (!st.assets || overlay.hidden && !seekTo) return;
  clearTimeout(resizeTimer);
  resizeTimer = setTimeout(() => {
    if (seekTo && st.state !== 'playing') { seek(seekTo); return; }
    if (st.state !== 'playing') return;
    computeViews();
    if (st.descent) { st.descent = computeDescent(); }
  }, 100);
});

async function boot() {
  const deck = window.deck;
  if (!deck) return;
  await deck.ready;
  if (deck.index !== 0) {                        // deep link: no intro; I still replays from #01
    overlay.dataset.boot = 'deep-link';
    loadAssets().catch(() => {});
    return;
  }
  if (mqReduced.matches && !seekTo) {
    overlay.dataset.boot = 'reduced-motion';
    loadAssets().catch(() => {});
    finalFrame();
    return;
  }
  const t0 = performance.now();
  try {
    await withTimeout(loadAssets(), ASSET_TIMEOUT_MS, 'intro maps');
  } catch (err) {
    overlay.dataset.boot = `assets-timeout ${Math.round(performance.now() - t0)}`;
    console.warn(`intro: ${err.message}; showing the title`);
    finalFrame();
    return;
  }
  st.log.push({ stage: 'assets', at: Math.round(performance.now() - t0) });
  overlay.dataset.boot = `assets ${Math.round(performance.now() - t0)}`;
  if (seekTo) { await seek(seekTo); return; }
  play();
}

boot().catch((err) => {
  console.error(err);
  finalFrame();
});
