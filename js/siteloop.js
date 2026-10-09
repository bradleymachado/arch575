/* ==========================================================================
   arch575.bradmachado.com — js/siteloop.js   (siteloop_v1.0, S17)
   This section is intended to play the slide 02 feature loop: on entering
   slide 02 (kind 'site', >= 900 px) the tower canvas goes full-viewport with
   the S14 site context greyed out (every context colour lerped 60 % toward
   the page background), one fixed oblique camera from the south-south-east
   (SITE_VIEW), and the named feature nodes of assets/site.glb cross-fade to
   the accent one at a time; the sixth step is the Site band, then the tower
   fades in as a ghost (js/tower.js ghostMode / setGhost: translucent pale
   fill + ink edges), holds, and the cycle restarts.

   Timing (plan §1 "Site loop timing", ms; ease-in-out-cubic):
     step i (0..5) starts at i x 2400: rise 400, hold 2000, fall 400 overlapping
     the next rise.  Steps: Randolph St (r_randolph), Restaurant Row
     (b_restaurantrow), Halsted St (r_halsted), Washington Blvd (r_washington),
     Skybridge (b_skybridge), 725 W Randolph (Site band).
     ghost rise 800 after the site band (14400-15200), site hold 8000
     (15200-23200), reset to grey 600 (23200-23800), cycle 23800, LOOP.
     LOOP = false holds on the site + ghost at 23200.

   Feature highlight = an overlay mesh per node (same geometry, child of the
   node mesh, flat MeshBasicMaterial in the accent, depthWrite off) whose
   opacity is the step's k; the greyed lit node stays underneath, so grey ->
   accent is a true cross-fade and reads flat on a projector. Mono caption
   bottom-left names the active feature; attribution line as the intro.

   Hooks: enter on deck change to #02 (also at boot on a deep link), leave on
   any other slide (colours, tower materials, camera, wrapper and photo
   restored); I on #02 restarts the loop (js/app.js); prefers-reduced-motion
   -> the static final frame (site + ghost); below 900 px, without WebGL, or
   if site.glb fails, the photo slide stays. Captures: ?loopat=1..6|ghost
   freezes the end state of that step (no animation).

   window.siteloop: .active, .state 'idle'|'loading'|'playing'|'static'|
   'frozen', .log, .t0, .cycle, .view, .nodes, .restart(), .stateAt(t)
   ========================================================================== */

const LOOP = true;
const TRANS_MS = 1500;                        // 01 <-> 02: one continuous shot (camera tween + tower dissolve)
const HOLD_SITE_MS = 8000;
const RISE_MS = 400, HOLD_MS = 2000, FALL_MS = 400;
const STEP_MS = RISE_MS + HOLD_MS;            // 2400: the fall overlaps the next rise
const GHOST_RISE_MS = 800;
const RESET_MS = 600;
const GREY_MS = 600;                          // grey-out tween on entering / leaving
const GREY_MIX = 0.6;                         // context colours this far toward the page background
const FIT_PAD = 0.04;                         // 4 % of the viewport on each side
const TOWER_TOP_M = 219.46 + 8;               // tower GLB height (plan §1) + margin (fit set only with FIT_TOWER_TOP)
const FIT_TOWER_TOP = false;                  // true: keep the whole ghost in frame (camera retreats ~3x)
const SITE_FILL = true;                       // flat accent fill of the Site polygon under the ghost (the GLB band is 1 ft wide)
const SITE_FILL_LIFT_FT = 1.5;                // above the terrain triangles under the site
const FT = 0.3048;
const DEG = Math.PI / 180;

const FEATURES = [
  { id: 'randolph', label: 'Randolph Street', node: 'r_randolph' },
  { id: 'restaurantrow', label: 'Restaurant Row', node: 'b_restaurantrow' },
  { id: 'halsted', label: 'Halsted Street', node: 'r_halsted' },
  { id: 'washington', label: 'Washington Boulevard', node: 'r_washington' },
  { id: 'skybridge', label: 'Skybridge', node: 'b_skybridge' },
  { id: 'site', label: '725 W Randolph', node: 'Site' },
];
const N = FEATURES.length;
const SITE_START = (N - 1) * STEP_MS;                 // 12000
const GHOST_AT = N * STEP_MS;                         // 14400
const RESET_AT = GHOST_AT + GHOST_RISE_MS + HOLD_SITE_MS;   // 23200
const CYCLE_MS = RESET_AT + RESET_MS;                 // 23800

// One fixed oblique view (Brad, 22:39): target = centre of the Site polygon; camera from the
// south-south-east, 20 deg east of due south (the title camera is 32 deg west of south; a shorter
// swing, 10 deg east, puts the Skybridge block in front of the site), pitch -30 deg; distance so that N Halsted St sits at
// the left third and the Kennedy Expressway at the right edge (frame x = halsted - 0.5 x (kennedyEast
// - halsted) .. kennedyEast; the depth follows the aspect, the ghost's top floors may crop); the
// principal point sits 8 % right of centre so the text column stays clear (setViewOffset, as #01).
// Distance and target are fitted at runtime (logged in .view).
const SITE_VIEW = {
  yawDeg: 195,                                        // 23:50 (Brad): from the east-north-east looking down Randolph, so 737 W Washington no longer stands between the camera and the site (was 110 = SSE)                                        // tower.js place(): offset (sin az, ., cos az); +x south, -z east -> az 110 = 20 deg east of south (title view 31.95 is SW: swing 78 deg; at 100 the Skybridge block covers the site)
  pitchDeg: -38,                                     // strategy session 23:20: -30 put two towers across the site; -42 shows the grid
  biasX: 0.08,
  kennedyEastFt: 250,                                 // east edge of the expressway = OSM centre + this
  frameFt: { x0: 979, x1: 1918, y0: 1198, y1: 1598 },   // defaults; site.json siteLoop.frameFt overrides
};

const mqSlides = window.matchMedia('(min-width: 900px)');
const mqReduced = window.matchMedia('(prefers-reduced-motion: reduce)');
const params = new URLSearchParams(location.search);
const freezeAt = params.get('loopat');

const easeInOutCubic = (t) => (t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2);
const clamp01 = (t) => Math.min(1, Math.max(0, t));
const smooth = (t, a, b) => easeInOutCubic(clamp01((t - a) / (b - a)));

const wrap = document.getElementById('tower-wrap');

/* --------------------------------------------------------------------------
   Caption block
   -------------------------------------------------------------------------- */

const meta = document.createElement('div');
meta.id = 'siteloop';
meta.hidden = true;
meta.setAttribute('aria-hidden', 'true');
meta.innerHTML = '<p class="siteloop__caption"></p><p class="siteloop__attribution"></p>';
// Large feature name over the feature itself (Brad, 23:50): projected centre of the active node
const nameEl = document.createElement('p');
nameEl.className = 'siteloop__name';
document.body.appendChild(nameEl);
document.body.append(meta);
const captionEl = meta.querySelector('.siteloop__caption');
const attributionEl = meta.querySelector('.siteloop__attribution');

const st = {
  active: false,
  state: 'idle',
  t0: 0,
  raf: 0,
  cycle: 0,
  log: [],
  seen: new Set(),
  nodes: null,          // { name: mesh }
  base: new Map(),      // material -> base colour
  grey: new Map(),      // material -> greyed colour
  greyK: 0,
  greyAnim: null,
  overlays: [],         // per feature: { mesh, mat } or null
  siteFill: null,       // { mesh, mat } accent plate of the Site polygon
  view: null,
  bg: null,
  accent: null,
  enterAt: 0,
  leaveTimer: 0,
  last: null,
  lastIndex: -1,
  trans: null,          // 01 <-> 02 transition in flight: { dir, t0, ms, from, to, dYaw, g0, minCtx, frames }
  transLog: [],
};

const siteloop = {
  get active() { return st.active; },
  get state() { return st.state; },
  get log() { return st.log.slice(); },
  get t0() { return st.t0; },
  get cycle() { return st.cycle; },
  get view() { return st.view; },
  get nodes() { return st.nodes ? Object.fromEntries(Object.entries(st.nodes).map(([k, m]) => [k, m.geometry.index ? m.geometry.index.count / 3 : m.geometry.attributes.position.count / 3])) : null; },
  get greyK() { return st.greyK; },
  get last() { return st.last; },
  get transition() { return st.trans ? { dir: st.trans.dir, at: Math.round(performance.now() - st.trans.t0) } : null; },
  get transLog() { return st.transLog.slice(); },
  // tower.js asks before applying its own slide rules: the loop owns #02 and the 02 -> 01 move
  handles(index, slide) {
    const tower = window.tower;
    if (!tower || tower.status === 'fallback' || !mqSlides.matches) return false;
    if (slide?.kind === 'site' && index === 1) return true;
    return index === 0 && (st.active || !!st.trans);
  },
  constants: { LOOP, HOLD_SITE_MS, STEP_MS, RISE_MS, HOLD_MS, FALL_MS, GHOST_RISE_MS, RESET_MS, CYCLE_MS, GREY_MIX },
  restart,
  stateAt,
  // checks / captures: apply the state at t ms (no animation) and render it
  applyAt(t) { stopLoop(); const s = stateAt(t); applyState(s); window.tower?.renderNow?.(); return s; },
  materials() { return st.nodes ? Object.entries(st.nodes).map(([name, m]) => ({ name, hex: '#' + m.material.color.getHexString() })) : null; },
  overlayState() { return st.overlays.map((o, i) => (o ? { node: FEATURES[i].node, visible: o.mesh.visible, opacity: +o.mat.opacity.toFixed(3) } : null)).concat(st.siteFill ? [{ node: 'sitefill', visible: st.siteFill.mesh.visible, opacity: +st.siteFill.mat.opacity.toFixed(3) }] : []); },
};
window.siteloop = siteloop;

/* --------------------------------------------------------------------------
   Timeline
   -------------------------------------------------------------------------- */

// State at t ms into a cycle: k per feature (0..1), ghost level, active caption
function stateAt(t) {
  const k = new Array(N).fill(0);
  for (let i = 0; i < N; i++) {
    const start = i * STEP_MS;
    const rise = smooth(t, start, start + RISE_MS);
    const fallStart = i < N - 1 ? start + STEP_MS : RESET_AT;
    const fallMs = i < N - 1 ? FALL_MS : RESET_MS;
    k[i] = rise * (1 - smooth(t, fallStart, fallStart + fallMs));
  }
  const ghost = smooth(t, GHOST_AT, GHOST_AT + GHOST_RISE_MS) * (1 - smooth(t, RESET_AT, RESET_AT + RESET_MS));
  let active = -1, best = 0;
  for (let i = 0; i < N; i++) if (k[i] > best) { best = k[i]; active = i; }
  const stage = t >= RESET_AT ? 'reset' : t >= GHOST_AT ? 'ghost' : FEATURES[Math.min(N - 1, Math.floor(t / STEP_MS))].id;
  return { t, k, ghost, active, captionK: best, stage };
}

function applyState(s) {
  for (let i = 0; i < N; i++) {
    const o = st.overlays[i];
    if (!o) continue;
    o.mat.opacity = s.k[i];
    o.mesh.visible = s.k[i] > 0;
  }
  if (st.siteFill) { st.siteFill.mat.opacity = s.k[N - 1]; st.siteFill.mesh.visible = s.k[N - 1] > 0; }
  window.tower?.ghostSetLevel?.(s.ghost);
  captionEl.textContent = s.active >= 0 ? FEATURES[s.active].label : '';
  captionEl.style.opacity = String(s.captionK);
  placeName(s);
  st.last = s;
}

// The big name: centred above the active feature's projected bounds centre (cached per node)
function placeName(s) {
  const tower = window.tower;
  if (s.active < 0 || !tower?.project) { nameEl.style.opacity = '0'; return; }
  const f = FEATURES[s.active];
  const node = st.nodes?.[f.node];
  if (!node) { nameEl.style.opacity = '0'; return; }
  const THREE = st.THREE;
  if (!THREE) { nameEl.style.opacity = '0'; return; }
  if (!node.userData.centre) node.userData.centre = new THREE.Box3().setFromObject(node).getCenter(new THREE.Vector3());
  const p = tower.project(node.userData.centre.clone());
  nameEl.textContent = f.label;
  nameEl.style.transform = `translate(${Math.round(p.x)}px, ${Math.round(p.y)}px) translate(-50%, -100%)`;
  nameEl.style.opacity = String(s.captionK);
}

/* --------------------------------------------------------------------------
   Context colours and overlays
   -------------------------------------------------------------------------- */

function cssColor(name, fallback) {
  const v = getComputedStyle(document.documentElement).getPropertyValue(name).trim();
  return v || fallback;
}

function prepareContext(THREE) {
  st.THREE = THREE;
  const tower = window.tower;
  st.nodes = tower.contextNodes();
  if (!st.nodes) return false;
  st.bg = new THREE.Color(cssColor('--color-bg', '#FCFCFA'));
  st.accent = new THREE.Color(cssColor('--color-accent', '#B0431F'));
  st.base.clear(); st.grey.clear();
  for (const [name, mesh] of Object.entries(st.nodes)) {
    const m = mesh.material;
    if (/^r_/.test(name) || st.base.has(m)) continue;     // street ribbons are accent-only (tower.js)
    const base = m.color.clone();
    st.base.set(m, base);
    st.grey.set(m, base.clone().lerp(st.bg, GREY_MIX));
  }
  // site fill: the Site polygon (data/site.json sitePolygonFt) as a flat accent plate just above grade
  st.siteFill?.mesh.removeFromParent();
  st.siteFill = null;
  const poly = tower.site?.sitePolygonFt;
  if (SITE_FILL && poly && tower.contextGroup) {
    const pts = poly.map(([X, Y]) => new THREE.Vector2(X, Y));
    const tris = THREE.ShapeUtils.triangulateShape(pts, []);
    const z = (tower.site.towerPlacement?.groundFt ?? 0) + SITE_FILL_LIFT_FT;
    const pos = new Float32Array(poly.flatMap(([X, Y]) => [X * FT, z * FT, -Y * FT]));
    const geo = new THREE.BufferGeometry();
    geo.setAttribute('position', new THREE.BufferAttribute(pos, 3));
    geo.setIndex(tris.flat());
    const mat = new THREE.MeshBasicMaterial({ color: st.accent, transparent: true, opacity: 0, depthWrite: false, side: THREE.DoubleSide });
    mat.name = 'siteloop:sitefill';
    const mesh = new THREE.Mesh(geo, mat);
    mesh.name = 'overlay:sitefill';
    mesh.userData.overlay = true;
    mesh.visible = false;
    mesh.renderOrder = 1;
    tower.contextGroup.add(mesh);
    st.siteFill = { mesh, mat };
  }
  // overlays: one per feature node (same geometry, accent, flat); ribbons drive their own node
  for (const o of st.overlays) if (o && !o.own) o.mesh.removeFromParent();
  st.overlays = FEATURES.map((f) => {
    const node = st.nodes[f.node];
    if (!node) return null;
    if (/^r_/.test(f.node)) {                   // ribbon: the node itself is the highlight
      node.material.color.copy(st.accent);
      node.material.opacity = 0;
      node.visible = false;
      return { mesh: node, mat: node.material, own: true };
    }
    const mat = new THREE.MeshBasicMaterial({ color: st.accent, transparent: true, opacity: 0, depthWrite: false, side: THREE.DoubleSide });
    mat.name = `siteloop:${f.node}`;
    const mesh = new THREE.Mesh(node.geometry, mat);
    mesh.name = `overlay:${f.node}`;
    mesh.userData.overlay = true;
    mesh.visible = false;
    mesh.renderOrder = 1;
    node.add(mesh);
    return { mesh, mat };
  });
  return true;
}

function applyGrey(k) {
  st.greyK = k;
  for (const [m, base] of st.base) m.color.copy(base).lerp(st.grey.get(m), k);
}

function tweenGrey(to, ms) {
  if (ms <= 0 || mqReduced.matches || st.greyK === to) { st.greyAnim = null; applyGrey(to); window.tower?.renderNow?.(); return; }
  st.greyAnim = { t0: performance.now(), from: st.greyK, to, ms };
  if (!st.raf) st.raf = requestAnimationFrame(tick);
}

function dropOverlays() {
  for (const o of st.overlays) {
    if (!o) continue;
    if (o.own) { o.mesh.visible = false; o.mat.opacity = 0; continue; }   // ribbon node stays, hidden
    o.mesh.removeFromParent();
    o.mat.dispose();
  }
  st.overlays = [];
  if (st.siteFill) { st.siteFill.mesh.removeFromParent(); st.siteFill.mat.dispose(); st.siteFill = null; }
}

/* --------------------------------------------------------------------------
   Camera
   -------------------------------------------------------------------------- */

function fitView() {
  const tower = window.tower;
  const site = tower.site;
  const g = site?.towerPlacement?.groundFt ?? 0;
  const f = { ...SITE_VIEW.frameFt };
  const sl = site?.siteLoop?.frameFt;
  if (sl && sl.halstedX != null && sl.kennedyX != null) {
    f.x1 = sl.kennedyX + SITE_VIEW.kennedyEastFt;
    f.x0 = sl.halstedX - 0.5 * (f.x1 - sl.halstedX);        // Halsted at the left third
    // a narrow band about Randolph, so the Halsted / Kennedy width governs the distance (the depth follows the aspect)
    if (sl.randolphY != null) { f.y0 = sl.randolphY - 450; f.y1 = sl.randolphY + 450; }
  }
  const corners = [[f.x0, f.y0], [f.x1, f.y0], [f.x1, f.y1], [f.x0, f.y1]].map(([X, Y]) => tower.modelFtToScene(X, Y, g));
  // the tower top is not in the fit set (Brad, 22:39: distance from Halsted / Kennedy); FIT_TOWER_TOP = true adds it
  if (FIT_TOWER_TOP) for (const [x, z] of [[0, 0], [97.84, 0], [97.84, 63.4], [0, 63.4]]) corners.push(tower.vec3(x, TOWER_TOP_M, z));
  // target = centre of the Site polygon (area centroid of data/site.json sitePolygonFt) at grade
  const poly = site?.sitePolygonFt;
  let cx = (f.x0 + f.x1) / 2, cy = (f.y0 + f.y1) / 2;
  if (poly?.length > 2) {
    let A = 0, sx = 0, sy = 0;
    for (let i = 0; i < poly.length; i++) {
      const [x0, y0] = poly[i], [x1, y1] = poly[(i + 1) % poly.length];
      const cr = x0 * y1 - x1 * y0; A += cr; sx += (x0 + x1) * cr; sy += (y0 + y1) * cr;
    }
    if (Math.abs(A) > 1e-9) { cx = sx / (3 * A); cy = sy / (3 * A); }
  }
  const c = tower.modelFtToScene(cx, cy, g);
  const target = [c.x, c.y, c.z];
  const r = wrap.getBoundingClientRect();
  const x0 = r.left + r.width * FIT_PAD, x1 = r.right - r.width * FIT_PAD;
  const y0 = r.top + r.height * FIT_PAD, y1 = r.bottom - r.height * FIT_PAD;
  const fits = (d) => {
    tower.setCamera({ yawDeg: SITE_VIEW.yawDeg, pitchDeg: SITE_VIEW.pitchDeg, distance: d, target });
    return corners.every((v) => { const p = tower.project(v); return p.z < 1 && p.x >= x0 && p.x <= x1 && p.y >= y0 && p.y <= y1; });
  };
  let lo = 10, hi = 4500;                             // camera far plane is 5000 (tower.js)
  for (let i = 0; i < 40; i++) { const mid = (lo + hi) / 2; if (fits(mid)) hi = mid; else lo = mid; }
  const view = { yawDeg: SITE_VIEW.yawDeg, pitchDeg: SITE_VIEW.pitchDeg, distance: +hi.toFixed(2), target: target.map((v) => +v.toFixed(2)), targetModelFt: [+cx.toFixed(2), +cy.toFixed(2)], biasX: SITE_VIEW.biasX, frameFt: f, viewport: [Math.round(r.width), Math.round(r.height)] };
  tower.setCamera(view);
  st.view = view;
  return view;
}

/* --------------------------------------------------------------------------
   01 <-> 02 transition: camera (yaw shortest path, pitch, log-distance, target), projection mix,
   solid tower dissolve, grey-out; 1.5 s ease-in-out-cubic. 'in' ends by starting the loop,
   'out' ends with slide 01 as the intro leaves it.
   -------------------------------------------------------------------------- */

function lerpView(a, b, e, dYaw) {
  return {
    yawDeg: a.yawDeg + dYaw * e,
    pitchDeg: a.pitchDeg + (b.pitchDeg - a.pitchDeg) * e,
    distance: a.distance * Math.pow(b.distance / a.distance, e),
    target: a.target.map((v, i) => v + (b.target[i] - v) * e),
  };
}

function startTransition(dir, from, to, g0 = 0) {
  const tower = window.tower;
  let dYaw = (((to.yawDeg - from.yawDeg) % 360) + 540) % 360 - 180;
  st.trans = { dir, t0: performance.now(), ms: TRANS_MS, from, to, dYaw, g0, minCtx: 1, frames: 0 };
  tower.setCamera(from);
  tower.setProjectionMix(dir === 'in' ? 0 : 1);   // 'in' starts on slide 01's grid-box projection
  if (!st.raf) st.raf = requestAnimationFrame(tick);
}

function stepTransition(now) {
  const tr = st.trans;
  const tower = window.tower;
  const k = Math.min(1, (now - tr.t0) / tr.ms);
  const e = easeInOutCubic(k);
  const a0 = performance.now();
  tower.setCamera(lerpView(tr.from, tr.to, e, tr.dYaw));
  tr.frames += 1;
  tr.minCtx = Math.min(tr.minCtx, tower.context.opacity);
  if (tr.dir === 'in') {
    tower.setProjectionMix(e);
    tower.setSolid(1 - e);
  } else {
    tower.setProjectionMix(1 - e);
    tower.setSolid(e);
    tower.setGhostEdges(tr.g0 * (1 - e));
  }
  tr.cost = (tr.cost || 0) + (performance.now() - a0);   // diagnostics: ms spent in the step itself
  (tr.times ||= []).push(Math.round(now - tr.t0));
  tr.renderMs = (tr.renderMs || 0) + (tower.lastRenderMs || 0);
  if (k >= 1) finishTransition();
}

function finishTransition() {
  const tr = st.trans;
  if (!tr) return;
  const tower = window.tower;
  st.trans = null;
  const entry = { dir: tr.dir, startAt: Math.round(tr.t0), ms: Math.round(performance.now() - tr.t0), frames: tr.frames, minContextOpacity: tr.minCtx, dYaw: +tr.dYaw.toFixed(2), stepCostMs: +(tr.cost || 0).toFixed(1), renderMsSum: +(tr.renderMs || 0).toFixed(1), times: tr.times || [] };
  if (tr.dir === 'in') {
    tower.setCamera(tr.to);
    tower.setProjectionMix(1);
    tower.setSolid(0);
    entry.towerOpacityEnd = tower.solid;
    tower.ghostMode(true);                     // hidden; the ghost rises at step 6
    tower.setSolid(1);                         // the neutral materials are not in use: keep them solid for later
    st.transLog.push(entry);
    if (st.active) startLoop();
  } else {
    tower.setCamera(null);
    tower.setSolid(1);
    tower.setGhostEdges(0);
    tower.setFull(mqSlides.matches && window.deck?.index === 0, 'box');
    tower.setContext(window.deck?.index === 0);
    entry.towerOpacityEnd = tower.solid;
    st.transLog.push(entry);
  }
}

/* --------------------------------------------------------------------------
   Sequence
   -------------------------------------------------------------------------- */

function tick(now) {
  st.raf = 0;
  if (st.trans) stepTransition(now);
  if (st.greyAnim) {
    const a = st.greyAnim;
    const k = Math.min(1, (now - a.t0) / a.ms);
    applyGrey(a.from + (a.to - a.from) * easeInOutCubic(k));
    if (k >= 1) st.greyAnim = null;
    window.tower?.renderNow?.();
  }
  if (st.state === 'playing') {
    const el = Math.max(0, now - st.t0);     // the first rAF timestamp can precede t0 by a fraction of a frame
    let t;
    if (LOOP) {
      const cyc = Math.floor(el / CYCLE_MS);
      if (cyc > st.cycle) { st.cycle = cyc; st.seen.clear(); st.log.push({ stage: 'cycle', n: cyc, at: Math.round(now - st.t0), sched: cyc * CYCLE_MS }); }
      t = el - cyc * CYCLE_MS;
    } else {
      t = Math.min(el, RESET_AT);
    }
    const s = stateAt(t);
    // stage log: first frame in which a stage is active (performance.now() relative to t0)
    const marks = [];
    for (let i = 0; i < N; i++) if (t >= i * STEP_MS) marks.push([FEATURES[i].id, i * STEP_MS]);
    if (t >= GHOST_AT) marks.push(['ghost', GHOST_AT]);
    if (t >= RESET_AT) marks.push(['reset', RESET_AT]);
    for (const [id, sched] of marks) {
      if (st.seen.has(id)) continue;
      st.seen.add(id);
      st.log.push({ stage: id, cycle: st.cycle, at: Math.round(now - st.t0), sched: st.cycle * CYCLE_MS + sched, frames: 0 });
    }
    st.log[st.log.length - 1].frames = (st.log[st.log.length - 1].frames || 0) + 1;
    applyState(s);
    window.tower?.renderNow?.();
    if (!LOOP && el >= RESET_AT) { st.state = 'static'; return; }
  }
  if (!st.raf && (st.state === 'playing' || st.greyAnim || st.trans)) st.raf = requestAnimationFrame(tick);   // one chain only (startLoop may have scheduled it)
}

function startLoop() {
  st.t0 = performance.now();
  st.cycle = 0;
  st.seen.clear();
  st.log = [{ stage: 'start', at: 0, sched: 0 }];
  st.state = 'playing';
  if (!st.raf) st.raf = requestAnimationFrame(tick);
}

function stopLoop() {
  if (st.raf) cancelAnimationFrame(st.raf);
  st.raf = 0;
}

// Static final frame (reduced motion) or a frozen step (?loopat=)
function freeze(id) {
  stopLoop();
  if (st.greyAnim) { applyGrey(st.greyAnim.to); st.greyAnim = null; }   // no animation frames in a frozen frame
  const t = id === 'ghost' ? GHOST_AT + GHOST_RISE_MS : /^[1-6]$/.test(id) ? (Number(id) - 1) * STEP_MS + RISE_MS : GHOST_AT + GHOST_RISE_MS;
  const s = stateAt(t);
  applyState(s);
  st.state = id === 'ghost' || !/^[1-6]$/.test(id) ? 'static' : 'frozen';
  st.last = s;
  window.tower?.renderNow?.();
  meta.dataset.frozen = id;
}

function restart() {
  if (!st.active) return;
  if (st.state === 'loading') return;
  if (mqReduced.matches) { freeze('ghost'); return; }
  const tower = window.tower;
  tower.setGhost(false, 0);
  startLoop();
  meta.dataset.restarted = String(Math.round(performance.now()));
}

/* --------------------------------------------------------------------------
   Enter / leave
   -------------------------------------------------------------------------- */

async function enter(fromIndex = -1) {
  if (st.active) return;
  if (st.trans) finishTransition();            // an 'out' still running: land it first
  st.active = true;
  st.state = 'loading';
  st.enterAt = performance.now();
  clearTimeout(st.leaveTimer);
  document.body.classList.add('is-siteloop');
  const tower = window.tower;
  await tower.ready;
  if (!st.active) return;
  if (tower.status === 'fallback' || !mqSlides.matches) { leave(); return; }
  // seamless from #01: the canvas is already full with the context up; one continuous shot
  const seamless = fromIndex === 0 && tower.full && tower.context.status === 'ready' && tower.context.opacity === 1 && !freezeAt && !mqReduced.matches && window.intro?.state !== 'playing';
  const from = seamless ? tower.titleView() : null;
  tower.setFull(true, 'viewport', { biasX: SITE_VIEW.biasX, mix: 1 });
  if (seamless) tower.setContext(true, 0);     // already 1: no fade
  else tower.setContext(true, fromIndex === 0 ? 0 : undefined);   // from #03+: fades in as before
  if (!seamless) tower.ghostMode(true);        // tower hidden until the ghost step
  fitView();                                   // with the final projection (mix 1)
  meta.hidden = false;
  captionEl.style.opacity = '0';
  attributionEl.textContent = tower.site?.attribution || 'Map data © OpenStreetMap contributors';
  if (seamless) startTransition('in', from, st.view);   // camera back to the title view at mix 0, then tweens
  const group = await tower.contextReady;
  if (!st.active) return;
  if (!group) { leave(); return; }
  const THREE = await import('three');
  if (!st.active) return;
  if (!prepareContext(THREE)) { leave(); return; }
  tweenGrey(1, seamless ? TRANS_MS : tower.context.opacity > 0 ? GREY_MS : 0);
  meta.dataset.ready = String(Math.round(performance.now() - st.enterAt));
  if (freezeAt || mqReduced.matches) tower.setContext(true, 0);   // static frames: no fade to wait for
  if (freezeAt) { freeze(freezeAt); return; }
  if (mqReduced.matches) { freeze('ghost'); return; }
  if (seamless) return;                        // finishTransition() starts the loop
  startLoop();
}

function leave(target = -1) {
  if (st.trans && !st.active) { finishTransition(); }
  if (!st.active) return;
  st.active = false;
  const wasLoading = st.state === 'loading';
  stopLoop();
  st.state = 'idle';
  meta.hidden = true;
  document.body.classList.remove('is-siteloop');
  const tower = window.tower;
  if (!tower) return;
  const g0 = tower.ghost.on ? tower.ghost.level : 0;
  const seamless = target === 0 && mqSlides.matches && st.view && tower.context.status === 'ready' && tower.context.opacity === 1 && !mqReduced.matches && !wasLoading;
  dropOverlays();
  if (st.trans) {                              // 'in' still running: reverse from where it is
    const tr = st.trans;
    st.trans = null;
    tower.setSolid(1); tower.ghostMode(false);
  }
  if (seamless) {
    // ghost (or empty) -> solid: the edges fade on their own while the solid tower comes back
    tower.ghostMode(false);
    tower.setGhostEdges(g0);
    tower.setSolid(0);
    tweenGrey(0, TRANS_MS);
    startTransition('out', { ...st.view }, tower.titleView(), g0);
    st.last = null;
    return;
  }
  tower.ghostMode(false);
  tower.setSolid(1);
  tower.setGhostEdges(0);
  tower.setCamera(null);
  // grey -> S15 colours: tween while the context is still visible (#01), else restore after its fade
  if (st.base.size) {
    if (target === 0) tweenGrey(0, GREY_MS);
    else st.leaveTimer = setTimeout(() => { if (!st.active) { applyGrey(0); tower.renderNow?.(); } }, 950);
  }
  // the wrapper: #01 keeps the full canvas (box mode), elsewhere its grid box
  tower.setFull(target === 0 && mqSlides.matches, 'box');
  tower.setContext(target === 0);
  st.last = null;
}

async function boot() {
  const deck = window.deck;
  if (!deck) return;
  await deck.ready;
  await window.tower?.ready;
  deck.on('change', (index, slide) => {
    const from = st.lastIndex;
    st.lastIndex = index;
    if (slide.kind === 'site' && index === 1 && mqSlides.matches) enter(from);
    else {
      if (st.trans && st.trans.dir === 'out' && index !== 0) finishTransition();   // 02 -> 01 -> elsewhere mid-tween
      leave(index);
    }
  });
  mqSlides.addEventListener('change', () => {
    const i = deck.index;
    if (i === 1 && mqSlides.matches) enter(); else if (st.active) leave(i);
  });
  let timer = 0;
  window.addEventListener('resize', () => {
    if (!st.active || st.state === 'loading') return;
    clearTimeout(timer);
    timer = setTimeout(() => { fitView(); window.tower?.renderNow?.(); }, 100);
  });
}

boot().catch((err) => console.error(err));
