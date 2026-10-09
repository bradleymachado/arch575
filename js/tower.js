/* ==========================================================================
   arch575.bradmachado.com — js/tower.js (S5)
   Loads assets/tower.glb once with three.js 0.186.1 (vendored, importmap in
   index.html), draws one accent highlight box per level and tweens the camera
   when js/app.js reports a slide change.

   Camera: yaw = camera.azDeg + orbitDeg x levelIndex (title and site slides
   use levelIndex 0), pitch = camera.pitchDeg, roll ignored. The look-at
   height eases toward the centre of the active level's y range, clamped so
   the whole tower stays in frame. Tween 900 ms ease-in-out-cubic, shortest
   angular path; instant under prefers-reduced-motion. Render on demand only
   (requestAnimationFrame while tweening or after a resize).

   Fallback: no WebGL, or the GLB fails -> assets/tower-fallback.png in
   #tower-wrap and a console warning.

   Public (for checks): window.tower
     .ready          Promise (resolves when the GLB is in the scene, or on fallback)
     .status         'loading' | 'ready' | 'fallback'
     .yaw, .targetY  current camera yaw (deg) and look-at height
     .yawFor(i)      yaw for levelIndex i
     .levels[i]      { key, bounds: {x0,x1,y0,y1,z0,z1}, mesh }   (bounds = box +- pad)
     .active         active levelIndex (-1 = none)
     .distance       camera distance from the look-at point
     .clamp          [yMin, yMax] allowed look-at heights at the current size
     .show(levelIndex, instant)  drive without the deck (check pages)

   S15 (tower_v1.0 additions). This section is intended to load assets/site.glb
   into the same scene as a 'context' group at the inverse of the tower
   placement (data/site.json towerOffset / towerYawDeg, so the tower stays at
   the origin), fade the context in on slide 01 and out over 900 ms on leaving
   it, and let js/intro.js drive the camera during the entry sequence:
     .siteReady / .contextReady   Promises (site.json parsed / site.glb in the scene or failed)
     .context        { status: 'none'|'loading'|'ready'|'failed', opacity, desired }
     .setContext(visible, ms)     fade the context (loads it on first request, >= 900 px only)
     .setFull(on)    #tower-wrap fills the viewport (class is-full); the projection stays
                     relative to the wrapper's grid box (setViewOffset), so the tower lands
                     exactly where the box camera puts it and the context fills the rest
     .box            that grid box {left, top, width, height} in viewport px
     .setCamera({yawDeg, pitchDeg, distance, target:[x,y,z]} | null)  camera override
     .titleView()    the deck's title camera in the same form
     .project(v3) -> {x, y} viewport px;  .modelFtToScene(X, Y, Z) site-model ft -> scene

   S17 (tower_v1.1 additions). This section is intended to give js/siteloop.js
   what the slide 02 feature loop needs: the context nodes by name (the S17
   site.glb carries b_skybridge, b_restaurantrow, buildings, r_randolph,
   r_halsted, r_washington, roads, TERRAIN_MESH, Bridges, Site), a whole-
   viewport projection mode for the full canvas, and the ghost tower:
     .setFull(on, mode, {biasX})   mode 'box' (default, S15: projection relative to the
                          grid box) or 'viewport' (the whole viewport is the frame; biasX
                          shifts the principal point right by that fraction of the width)
     .contextNodes()      { name: Mesh } for the context group (null before it loads)
     .contextGroup        the context Group (children in site.glb scene space)
     .ghostMode(on)       swap the tower's materials for one translucent pale fill
                          (opacity 0.30 x level, depthWrite off) + EdgesGeometry lines
                          in ink (opacity 0.5 x level); level starts at 0 (tower hidden);
                          off restores the S5 neutral materials at once
     .setGhost(on, ms)    tween the ghost level to 1 / 0 over ms (turns ghost mode on)
     .ghostSetLevel(k)    set the level directly (the loop drives it per frame)
     .setSolid(k)         the solid tower's opacity level 1..0 (the 01 <-> 02 dissolve)
     .setGhostEdges(k)    the ghost edges alone (02 -> 01: edges fade as the solid tower returns)
     .setProjectionMix(k) viewport mode: 0 = grid-box projection, 1 = whole viewport (01 <-> 02 tween)
     The deck handler defers to window.siteloop.handles(index, slide) for slide 02 and the 02 -> 01 move.
     .ghost               { on, level, opacity, edgeOpacity, edges }
   ========================================================================== */

import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';

const GLB_URL = 'assets/tower.glb';
const DATA_URL = 'data/levels.json';
const FALLBACK_URL = 'assets/tower-fallback.png';
const SITE_URL = 'data/site.json';     // S15: tower placement in the site model
const CTX_URL = 'assets/site.glb';     // S15: site context (buildings, terrain, bridges, roads, site band)
const CTX_FADE_MS = 900;
const FT = 0.3048;
const UNLIT = /^(TERRAIN_MESH|Roads|roads)$/; // flat ground nodes: unlit, so the terrain triangulation does not read
const RIBBON = /^r_(randolph|halsted|washington)$/;   // S17 street ribbons: accent, hidden until the loop raises them
const mqSlides = window.matchMedia('(min-width: 900px)');

const FOV = 28;            // deg, vertical
const PAD = 0.5;           // highlight box pad in x and z (glTF units)
const EPS = 0.02;          // extra offset outside the facade / slabs (z-fighting)
const FIT_PAD = 0.06;      // 6 % of the canvas on each side
const TWEEN_MS = 900;
const DEG = Math.PI / 180;

const wrap = document.getElementById('tower-wrap');
const canvas = document.getElementById('tower');
// Read at call time: the OS setting can change while the page is open
const reducedMotion = () => window.matchMedia('(prefers-reduced-motion: reduce)').matches;

const state = {
  status: 'loading',
  yaw: 0,
  targetY: 0,
  active: -1,
  distance: 0,
  clamp: [0, 0],
  levels: [],
  readyMs: 0,
  // S15
  pitch: 0,
  override: null,      // { yawDeg, pitchDeg, distance, target: [x, y, z] } while the intro drives the camera
  full: false,         // #tower-wrap fills the viewport (slide 01 at >= 900 px)
  box: null,           // the wrapper's grid box in viewport px (projection reference)
  ctx: { status: 'none', desired: false, opacity: 0, group: null, mats: [], anim: null },
  site: null,
  // S17
  fullMode: 'box',     // 'box' | 'viewport' (see setFull)
  viewBias: 0,
  projMix: 1,          // viewport mode: 0 = the grid-box projection (as 'box'), 1 = the whole viewport (tween 01 <-> 02)
  solid: 1,            // tower materials' opacity level (1 solid, 0 invisible)
  boxCache: null,      // { w, h, box } grid box measured at the last resize
  solidMats: [],
  ghost: { on: false, level: 0, anim: null, fill: null, edges: [], saved: null, built: false },
};

let resolveReady;
const ready = new Promise((res) => { resolveReady = res; });
let resolveSite, resolveContext;
const siteReady = new Promise((res) => { resolveSite = res; });
const contextReady = new Promise((res) => { resolveContext = res; });
let ctxInv = null;     // site.glb scene -> tower frame (inverse of the tower placement)
const hooks = {};      // filled by main(): requestFrame, resize, loadContext, fadeContext

const tower = {
  ready,
  get status() { return state.status; },
  get yaw() { return state.yaw; },
  get targetY() { return state.targetY; },
  get active() { return state.active; },
  get distance() { return state.distance; },
  get clamp() { return state.clamp.slice(); },
  get levels() { return state.levels; },
  get readyMs() { return state.readyMs; },
  yawFor: () => 0,
  show: () => {},
  // S15 intro API (usable before the GLB is in the scene; main() applies the stored state)
  get pitch() { return state.override ? state.override.pitchDeg : state.pitch; },
  get context() { return { status: state.ctx.status, opacity: state.ctx.opacity, desired: state.ctx.desired }; },
  get full() { return state.full; },
  get box() { return state.box ? { ...state.box } : null; },
  get site() { return state.site; },
  siteReady,
  contextReady,
  setFull(on, mode = 'box', { biasX = 0, mix = 1 } = {}) {
    state.full = !!on;
    state.fullMode = mode === 'viewport' ? 'viewport' : 'box';
    state.viewBias = +biasX || 0;              // viewport mode: principal point shifted right by this fraction of the width
    state.projMix = Math.min(1, Math.max(0, +mix));
    wrap?.classList.toggle('is-full', state.full);
    hooks.resize?.();
  },
  // S17
  get fullMode() { return state.fullMode; },
  get projMix() { return state.projMix; },
  get solid() { return state.solid; },
  setProjectionMix(k) { state.projMix = Math.min(1, Math.max(0, +k || 0)); hooks.applyProjection?.(); hooks.requestFrame?.(); },
  setSolid(level) { hooks.setSolid?.(Math.min(1, Math.max(0, +level || 0))); },
  setGhostEdges(level) { hooks.setGhostEdges?.(Math.min(1, Math.max(0, +level || 0))); },
  get ghost() {
    const g = state.ghost;
    return { on: g.on, level: g.level, opacity: +(GHOST_OPACITY * g.level).toFixed(4), edgeOpacity: +(GHOST_EDGE_OPACITY * g.level).toFixed(4), edges: g.edges.length };
  },
  get contextGroup() { return state.ctx.group; },   // children sit in site.glb scene space (m, y up, z = -north)
  contextNodes() {
    const g = state.ctx.group;
    if (!g) return null;
    const out = {};
    g.traverse((o) => { if (o.isMesh && !o.userData.overlay) out[o.name] = o; });
    return out;
  },
  ghostMode(on) { hooks.ghostMode?.(!!on); },
  setGhost(on, ms = GHOST_MS) { hooks.setGhost?.(!!on, ms); },
  ghostSetLevel(level) { hooks.ghostSetLevel?.(Math.min(1, Math.max(0, +level || 0))); },
  setCamera(view) {
    state.override = view ? { ...view, target: [...view.target] } : null;
    hooks.requestFrame?.();
  },
  setContext(visible, ms = CTX_FADE_MS) {
    state.ctx.desired = !!visible;
    if (visible) hooks.loadContext?.();
    hooks.fadeContext?.(ms);
  },
  loadContext() { hooks.loadContext?.(); return contextReady; },
  titleView: () => null,
  project: () => null,
  modelFtToScene(X, Y, Z) {
    if (!ctxInv) return null;
    return new THREE.Vector3(X * FT, Z * FT, -Y * FT).applyMatrix4(ctxInv);
  },
};
window.tower = tower;

const easeInOutCubic = (t) => (t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2);

/* --------------------------------------------------------------------------
   Fallback
   -------------------------------------------------------------------------- */

function fallback(reason) {
  console.warn(`tower: ${reason}; showing ${FALLBACK_URL}`);
  state.status = 'fallback';
  if (wrap) {
    const img = document.createElement('img');
    img.src = FALLBACK_URL;
    img.alt = '';
    img.className = 'deck__tower-fallback';
    wrap.classList.add('is-fallback');
    wrap.append(img);
  }
  if (canvas) canvas.hidden = true;
  resolveReady();
}

function webglAvailable() {
  try {
    const c = document.createElement('canvas');
    return !!(c.getContext('webgl2') || c.getContext('webgl'));
  } catch {
    return false;
  }
}

/* --------------------------------------------------------------------------
   Model materials. The GLB carries textured SketchUp materials (chipboard
   slab edges, concrete, two glasses) under KHR_materials_pbrSpecularGlossiness,
   which three.js no longer reads; the metallic-roughness fallback still shows
   the wood and blue-glass hues. The site allows one hue (the accent), so each
   material is replaced by a flat neutral grey of a similar tone; the model's
   geometry and material assignments are kept.
   -------------------------------------------------------------------------- */

const GHOST_FILL = 0xe4e4e2;       // S17 ghost: pale fill (palette grey), opacity GHOST_OPACITY
const GHOST_OPACITY = 0.30;
const GHOST_EDGE = 0x171715;       // ink edges
const GHOST_EDGE_OPACITY = 0.5;
const GHOST_EDGE_ANGLE = 20;       // EdgesGeometry threshold, degrees
const GHOST_MS = 800;

const GREYS = [
  [/chipboard/i, 0x9a9a9a, 1],
  [/concrete/i,  0xb5b5b5, 1],
  [/frosted/i,   0xe4e4e2, 1],
  [/glass/i,     0xf2f2f0, 0.35],
];

function neutralise(root) {
  const cache = new Map();
  root.traverse((o) => {
    if (!o.isMesh) return;
    const src = o.material;
    if (!cache.has(src)) {
      const name = src.name || '';
      const [, hex, opacity] = GREYS.find(([re]) => re.test(name)) || [null, 0xd9d9d9, 1];
      const m = new THREE.MeshStandardMaterial({
        color: hex,
        roughness: 0.95,
        metalness: 0,
        side: src.side ?? THREE.FrontSide,
        transparent: opacity < 1,
        opacity,
      });
      m.name = `neutral:${name}`;
      cache.set(src, m);
    }
    o.material = cache.get(src);
  });
  for (const src of cache.keys()) {
    for (const k of ['map', 'normalMap', 'metalnessMap', 'roughnessMap', 'emissiveMap', 'alphaMap']) src[k]?.dispose?.();
    src.dispose?.();
  }
  state.solidMats = [...cache.values()].map((m) => { m.userData.baseOpacity = m.opacity; return m; });
}

/* --------------------------------------------------------------------------
   Scene
   -------------------------------------------------------------------------- */

async function main() {
  if (!wrap || !canvas) return;
  if (!webglAvailable()) return fallback('WebGL is not available');

  let renderer;
  try {
    renderer = new THREE.WebGLRenderer({ canvas, alpha: true, antialias: true });
  } catch (err) {
    return fallback(`WebGL renderer failed (${err.message})`);
  }
  renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
  renderer.setClearColor(0x000000, 0);

  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(FOV, 1, 1, 5000);
  scene.add(camera);

  scene.add(new THREE.HemisphereLight(0xffffff, 0x8c8c8c, 2.2));
  const sun = new THREE.DirectionalLight(0xffffff, 1.6);
  sun.position.set(-0.55, 0.9, 1).normalize();   // upper left of the viewer, follows the camera
  camera.add(sun);

  // Data (from the deck when present, else straight from levels.json)
  const deck = window.deck;
  let data;
  try {
    data = deck ? await deck.ready : await (await fetch(DATA_URL)).json();
  } catch (err) {
    return fallback(`levels.json failed (${err.message})`);
  }
  const accent = new THREE.Color(data.accent);
  const yaw0 = data.camera.azDeg;
  const pitch = data.camera.pitchDeg;
  const orbit = data.orbitDeg;
  tower.yawFor = (i) => yaw0 + orbit * i;
  state.pitch = pitch;

  // S15: tower placement in the site model (small fetch, not awaited before the tower)
  const siteJson = fetch(SITE_URL)
    .then((r) => (r.ok ? r.json() : null))
    .catch(() => null)
    .then((site) => {
      state.site = site;
      if (site?.towerOffset) {
        const place = new THREE.Matrix4().compose(
          new THREE.Vector3(...site.towerOffset),
          new THREE.Quaternion().setFromAxisAngle(new THREE.Vector3(0, 1, 0), site.towerYawDeg * DEG),
          new THREE.Vector3(1, 1, 1),
        );
        ctxInv = place.invert();
      }
      resolveSite(site);
      return site;
    });

  // Highlight boxes: plan box +- pad in x and z, the level's y range, plus a
  // 0.02 offset outside every face so the box clears the facade and slabs.
  const boxMat = new THREE.MeshStandardMaterial({ color: accent, roughness: 0.9, metalness: 0 });
  const boxes = new THREE.Group();
  boxes.name = 'highlight';
  state.levels = data.levels.map((lv, i) => {
    const [bx0, bx1, bz0, bz1] = lv.box;
    const [y0, y1] = lv.y;
    const bounds = { x0: bx0 - PAD, x1: bx1 + PAD, y0, y1, z0: bz0 - PAD, z1: bz1 + PAD };
    const geo = new THREE.BoxGeometry(
      bounds.x1 - bounds.x0 + 2 * EPS,
      bounds.y1 - bounds.y0 + 2 * EPS,
      bounds.z1 - bounds.z0 + 2 * EPS,
    );
    const mesh = new THREE.Mesh(geo, boxMat);
    mesh.position.set((bounds.x0 + bounds.x1) / 2, (bounds.y0 + bounds.y1) / 2, (bounds.z0 + bounds.z1) / 2);
    mesh.name = `box-${lv.key}`;
    mesh.visible = false;
    mesh.userData = { key: lv.key, levelIndex: i, bounds };
    boxes.add(mesh);
    return { key: lv.key, bounds, mesh };
  });

  // Model
  let gltf;
  try {
    gltf = await new GLTFLoader().loadAsync(GLB_URL);
  } catch (err) {
    renderer.dispose();
    return fallback(`GLB failed to load (${err.message || err})`);
  }
  neutralise(gltf.scene);
  scene.add(gltf.scene);
  scene.add(boxes);
  state.readyMs = performance.now();

  const bb = new THREE.Box3().setFromObject(gltf.scene);
  const centre = bb.getCenter(new THREE.Vector3());
  const corners = [];
  for (const x of [bb.min.x, bb.max.x]) {
    for (const y of [bb.min.y, bb.max.y]) {
      for (const z of [bb.min.z, bb.max.z]) corners.push(new THREE.Vector3(x, y, z));
    }
  }

  /* ---- camera placement and framing ------------------------------------ */

  const target = new THREE.Vector3().copy(centre);

  function place(cam, tgt, yawDeg, dist, pitchDeg = pitch) {
    const az = yawDeg * DEG;
    const p = pitchDeg * DEG;
    cam.position.set(
      tgt.x + dist * Math.cos(p) * Math.sin(az),
      tgt.y - dist * Math.sin(p),
      tgt.z + dist * Math.cos(p) * Math.cos(az),
    );
    cam.lookAt(tgt);
    cam.updateMatrixWorld(true);
  }

  // Does the whole tower fit (with the padding) for every yaw at this
  // distance and look-at height?
  const probe = new THREE.PerspectiveCamera(FOV, 1, 1, 5000);
  const tmpT = new THREE.Vector3();
  const tmpV = new THREE.Vector3();
  const YAW_SAMPLES = 36;
  function fits(dist, targetY) {
    probe.aspect = camera.aspect;
    probe.updateProjectionMatrix();
    tmpT.set(centre.x, targetY, centre.z);
    const lim = 1 - 2 * FIT_PAD;
    for (let s = 0; s < YAW_SAMPLES; s++) {
      place(probe, tmpT, (360 * s) / YAW_SAMPLES, dist);
      for (const c of corners) {
        tmpV.copy(c).project(probe);
        if (Math.abs(tmpV.x) > lim || Math.abs(tmpV.y) > lim) return false;
      }
    }
    return true;
  }

  function refit() {
    // Smallest distance at which the tower fits at the centre look-at.
    let lo = 1, hi = 20000;
    for (let i = 0; i < 40; i++) {
      const mid = (lo + hi) / 2;
      if (fits(mid, centre.y)) hi = mid; else lo = mid;
    }
    state.distance = hi;
    // Allowed look-at range at that distance (monotonic away from the centre).
    const range = (dir) => {
      let a = 0, b = bb.max.y - bb.min.y;
      for (let i = 0; i < 30; i++) {
        const mid = (a + b) / 2;
        if (fits(state.distance, centre.y + dir * mid)) a = mid; else b = mid;
      }
      return centre.y + dir * a;
    };
    state.clamp = [range(-1), range(1)];
  }

  function targetYFor(levelIndex) {
    if (levelIndex < 0) return centre.y;
    const { y0, y1 } = state.levels[levelIndex].bounds;
    const y = (y0 + y1) / 2;
    return Math.min(state.clamp[1], Math.max(state.clamp[0], y));
  }

  /* ---- render on demand ------------------------------------------------- */

  let rafId = 0;
  let anim = null;

  // Camera placement: the intro's override when set, else the deck state
  function aim() {
    const o = state.override;
    if (o) {
      target.set(o.target[0], o.target[1], o.target[2]);
      place(camera, target, o.yawDeg, o.distance, o.pitchDeg);
    } else {
      target.set(centre.x, state.targetY, centre.z);
      place(camera, target, state.yaw, state.distance);
    }
  }

  function render() {
    aim();
    const a0 = performance.now();
    renderer.render(scene, camera);
    tower.lastRenderMs = performance.now() - a0;
  }

  /* ---- S15: site context ------------------------------------------------ */

  function applyCtxOpacity(k) {
    const c = state.ctx;
    c.opacity = k;
    c.group.visible = k > 0;
    for (const m of c.mats) {
      const t = k < 1;
      if (m.transparent !== t) { m.transparent = t; m.needsUpdate = true; }
      m.opacity = k;
    }
  }

  function fadeContext(ms = CTX_FADE_MS) {
    const c = state.ctx;
    if (c.status !== 'ready') return;
    const to = c.desired ? 1 : 0;
    if (ms <= 0 || reducedMotion() || c.opacity === to) {
      c.anim = null;
      applyCtxOpacity(to);
      requestFrame();
      return;
    }
    c.anim = { t0: performance.now(), from: c.opacity, to, ms };
    requestFrame();
  }

  async function loadContext() {
    const c = state.ctx;
    if (c.status !== 'none') return;
    if (!mqSlides.matches) return;              // below 900 px only the map stages play: no 6.6 MB context
    c.status = 'loading';
    await siteJson;
    if (!ctxInv) { c.status = 'failed'; console.warn('tower: site.json has no towerOffset; no context'); resolveContext(null); return; }
    let g;
    try {
      g = await new GLTFLoader().loadAsync(CTX_URL);
    } catch (err) {
      c.status = 'failed';
      console.warn(`tower: site.glb failed (${err.message || err}); no context`);
      resolveContext(null);
      return;
    }
    const group = new THREE.Group();
    group.name = 'context';
    group.add(g.scene);
    group.applyMatrix4(ctxInv);                  // tower stays at the origin; the site moves around it
    const mats = new Map();
    const ribbons = [];
    g.scene.traverse((o) => {
      if (!o.isMesh) return;
      const src = o.material;
      if (RIBBON.test(o.name)) {
        // S17: street ribbon 0.4 m above the road, flat accent, no depth write, polygon offset (never z-fights);
        // invisible until js/siteloop.js drives its opacity; not part of the context fade
        const m = new THREE.MeshBasicMaterial({ color: accent, transparent: true, opacity: 0, depthWrite: false, side: THREE.DoubleSide, polygonOffset: true, polygonOffsetFactor: -2, polygonOffsetUnits: -2 });
        m.name = `ribbon:${o.name}`;
        o.material = m;
        o.visible = false;
        o.renderOrder = 1;
        ribbons.push(src);
        return;
      }
      if (!mats.has(src)) {
        const color = src.color ? src.color.clone() : new THREE.Color(0xd9d9d9);
        const m = UNLIT.test(o.name)
          ? new THREE.MeshBasicMaterial({ color, side: THREE.DoubleSide })
          : new THREE.MeshStandardMaterial({ color, roughness: 0.95, metalness: 0, flatShading: true, side: THREE.DoubleSide });
        m.name = `context:${o.name}`;
        mats.set(src, m);
      }
      o.material = mats.get(src);
    });
    for (const src of mats.keys()) src.dispose?.();
    for (const src of ribbons) src.dispose?.();
    c.group = group;
    c.mats = [...mats.values()];
    c.opacity = 0;
    group.visible = false;
    scene.add(group);
    c.status = 'ready';
    resolveContext(group);
    fadeContext(CTX_FADE_MS);
  }
  hooks.loadContext = loadContext;
  hooks.fadeContext = fadeContext;

  /* ---- S17: ghost tower ------------------------------------------------- */

  const ghostObjects = [];                     // meshes of the tower GLB
  gltf.scene.traverse((o) => { if (o.isMesh) ghostObjects.push(o); });

  function buildGhost() {
    const g = state.ghost;
    if (g.built) return;
    g.fill = new THREE.MeshBasicMaterial({ color: GHOST_FILL, transparent: true, opacity: 0, depthWrite: false });
    g.fill.name = 'ghost:fill';
    const edgeMat = new THREE.LineBasicMaterial({ color: GHOST_EDGE, transparent: true, opacity: 0 });
    edgeMat.name = 'ghost:edges';
    for (const o of ghostObjects) {
      const lines = new THREE.LineSegments(new THREE.EdgesGeometry(o.geometry, GHOST_EDGE_ANGLE), edgeMat);
      lines.name = `ghost-edges:${o.name}`;
      lines.visible = false;
      lines.renderOrder = 2;
      o.add(lines);                            // follows the mesh transform
      g.edges.push(lines);
    }
    g.edgeMat = edgeMat;
    g.built = true;
  }

  function applyGhostLevel(level) {
    const g = state.ghost;
    g.level = level;
    if (!g.on) return;
    g.fill.opacity = GHOST_OPACITY * level;
    g.edgeMat.opacity = GHOST_EDGE_OPACITY * level;
    const vis = level > 0;
    gltf.scene.visible = vis;
    for (const l of g.edges) l.visible = vis;
  }

  function ghostMode(on) {
    const g = state.ghost;
    if (on === g.on) return;
    if (on) {
      buildGhost();
      g.saved = ghostObjects.map((o) => o.material);
      for (const o of ghostObjects) o.material = g.fill;
      g.on = true;
      g.anim = null;
      applyGhostLevel(0);                      // hidden until setGhost(true)
    } else {
      ghostObjects.forEach((o, i) => { o.material = g.saved?.[i] ?? o.material; });
      for (const l of g.edges) l.visible = false;
      gltf.scene.visible = state.solid > 0;
      g.on = false;
      g.anim = null;
      g.level = 0;
      g.saved = null;
    }
    requestFrame();
  }

  function setGhost(on, ms) {
    const g = state.ghost;
    if (!g.on) ghostMode(true);
    const to = on ? 1 : 0;
    if (ms <= 0 || reducedMotion() || g.level === to) {
      g.anim = null;
      applyGhostLevel(to);
      requestFrame();
      return;
    }
    g.anim = { t0: performance.now(), from: g.level, to, ms };
    requestFrame();
  }
  hooks.ghostMode = ghostMode;
  hooks.setGhost = setGhost;
  hooks.ghostSetLevel = (level) => { if (!state.ghost.on) ghostMode(true); state.ghost.anim = null; applyGhostLevel(level); requestFrame(); };

  // S17: the solid tower's opacity level (the 01 <-> 02 dissolve); depthWrite off below 1
  hooks.setSolid = (level) => {
    state.solid = level;
    for (const m of state.solidMats) {
      const base = m.userData.baseOpacity ?? 1;
      m.opacity = base * level;
      const t = level < 1 || base < 1;
      if (m.transparent !== t) { m.transparent = t; m.needsUpdate = true; }
      m.depthWrite = level >= 1;
    }
    if (!state.ghost.on) gltf.scene.visible = level > 0;
    requestFrame();
  };
  // S17: ghost edges on their own (the 02 -> 01 return: edges fade while the solid tower comes back)
  hooks.setGhostEdges = (level) => {
    const g = state.ghost;
    buildGhost();
    g.edgeMat.opacity = GHOST_EDGE_OPACITY * level;
    for (const l of g.edges) l.visible = level > 0;
    requestFrame();
  };

  function frame() {
    rafId = 0;
    const c = state.ctx;
    if (c.anim) {
      const k = Math.min(1, (performance.now() - c.anim.t0) / c.anim.ms);
      applyCtxOpacity(c.anim.from + (c.anim.to - c.anim.from) * k);
      if (k >= 1) c.anim = null;
    }
    const g = state.ghost;
    if (g.anim) {
      const k = Math.min(1, (performance.now() - g.anim.t0) / g.anim.ms);
      applyGhostLevel(g.anim.from + (g.anim.to - g.anim.from) * easeInOutCubic(k));
      if (k >= 1) g.anim = null;
    }
    if (anim) {
      const k = Math.min(1, (performance.now() - anim.t0) / TWEEN_MS);
      const e = easeInOutCubic(k);
      state.yaw = anim.yawFrom + anim.dYaw * e;
      state.targetY = anim.yFrom + anim.dY * e;
      if (k >= 1) {
        state.yaw = anim.yawTo;
        state.targetY = anim.yTo;
        anim = null;
      }
    }
    render();
    if (anim || state.ctx.anim || state.ghost.anim) requestFrame();
  }

  function requestFrame() {
    if (!rafId) rafId = requestAnimationFrame(frame);
  }
  hooks.requestFrame = requestFrame;
  tower.renderNow = () => { render(); };        // synchronous frame (captures under virtual time)

  tower.titleView = () => ({
    yawDeg: tower.yawFor(0),
    pitchDeg: pitch,
    distance: state.distance,
    target: [centre.x, targetYFor(-1), centre.z],
  });

  tower.vec3 = (x, y, z) => new THREE.Vector3(x, y, z);
  tower.projection = () => ({ aspect: +camera.aspect.toFixed(4), fov: camera.fov, view: camera.view ? { ...camera.view } : null, size: [wrap.clientWidth, wrap.clientHeight], full: state.full, mode: state.fullMode, mix: state.projMix, bias: state.viewBias, override: state.override, box: state.box });

  // World-space bounds of the context group (checks)
  tower.contextBounds = () => {
    const g = state.ctx.group;
    if (!g) return null;
    g.updateMatrixWorld(true);
    const b = new THREE.Box3().setFromObject(g);
    return { min: b.min.toArray(), max: b.max.toArray() };
  };

  // Viewport px of a scene point under the current camera placement
  tower.project = (v) => {
    aim();
    const p = v.clone().project(camera);
    const r = canvas.getBoundingClientRect();
    return { x: r.left + ((p.x + 1) / 2) * r.width, y: r.top + ((1 - p.y) / 2) * r.height, z: p.z };
  };

  function setActive(levelIndex) {
    state.active = levelIndex;
    state.levels.forEach((lv, k) => { lv.mesh.visible = k === levelIndex; });
  }

  // levelIndex -1 = title/site (no box, yaw index 0)
  function show(levelIndex, instant = false) {
    setActive(levelIndex);
    const yawTo = tower.yawFor(Math.max(0, levelIndex));
    const yTo = targetYFor(levelIndex);
    if (instant || reducedMotion()) {
      anim = null;
      state.yaw = yawTo;
      state.targetY = yTo;
      requestFrame();
      return;
    }
    const yawFrom = state.yaw;
    let dYaw = (((yawTo - yawFrom) % 360) + 540) % 360 - 180;   // shortest path
    if (Math.abs(Math.abs(dYaw) - 180) < 1e-9) dYaw = 180;
    anim = { t0: performance.now(), yawFrom, dYaw, yawTo, yFrom: state.targetY, dY: yTo - state.targetY, yTo };
    requestFrame();
  }
  tower.show = show;

  /* ---- size ------------------------------------------------------------- */

  // The wrapper's grid box while it is fixed full-viewport (class is-full):
  // drop the class, measure, put it back (one synchronous layout, no paint).
  function boxRect() {
    wrap.classList.remove('is-full');
    const r = wrap.getBoundingClientRect();
    wrap.classList.add('is-full');
    return r;
  }

  // Projection while the wrapper is full-viewport: 'box' = as if the canvas were still the grid box (S15);
  // 'viewport' = the whole viewport, principal point shifted by viewBias; projMix blends the two (01 <-> 02 tween)
  function applyProjection() {
    const w = wrap.clientWidth;
    const h = wrap.clientHeight;
    if (!w || !h) return false;
    const fixed = state.full && getComputedStyle(wrap).position === 'fixed';
    // the grid box is measured once per resize (boxRect forces a layout); per-frame mix changes reuse it
    if (fixed && (!state.boxCache || state.boxCache.w !== w || state.boxCache.h !== h)) { const b = boxRect(); state.boxCache = { w, h, box: { left: b.left, top: b.top, width: b.width, height: b.height } }; }
    const box = fixed ? state.boxCache.box : null;
    const boxP = box && box.width > 0 && box.height > 0 ? { fw: box.width, fh: box.height, ox: -box.left, oy: -box.top } : null;
    const vpP = { fw: w, fh: h, ox: -(state.fullMode === 'viewport' ? state.viewBias : 0) * w, oy: 0 };
    let P = vpP;
    if (fixed && boxP) {
      if (state.fullMode === 'box') P = boxP;
      else {
        const k = state.projMix;
        P = { fw: boxP.fw + (vpP.fw - boxP.fw) * k, fh: boxP.fh + (vpP.fh - boxP.fh) * k, ox: boxP.ox + (vpP.ox - boxP.ox) * k, oy: boxP.oy + (vpP.oy - boxP.oy) * k };
      }
    }
    camera.aspect = P.fw / P.fh;
    if (P === vpP && !P.ox) camera.clearViewOffset(); else camera.setViewOffset(P.fw, P.fh, P.ox, P.oy, w, h);
    if (fixed && boxP && state.fullMode === 'box') state.box = { left: box.left, top: box.top, width: box.width, height: box.height };
    else { const r = canvas.getBoundingClientRect(); state.box = { left: r.left, top: r.top, width: w, height: h }; }
    camera.updateProjectionMatrix();
    return true;
  }
  hooks.applyProjection = applyProjection;

  function resize() {
    const w = wrap.clientWidth;
    const h = wrap.clientHeight;
    if (!w || !h) return;
    renderer.setSize(w, h, false);
    state.boxCache = null;
    if (!applyProjection()) return;
    refit();
    if (!anim) state.targetY = targetYFor(state.active);
    requestFrame();
  }
  hooks.resize = resize;

  new ResizeObserver(resize).observe(wrap);
  resize();

  /* ---- deck ------------------------------------------------------------- */

  let first = true;
  state.status = 'ready';
  if (deck) {
    deck.on('change', (index, slide) => {
      show(slide.levelIndex, first);
      first = false;
      // S17: js/siteloop.js owns the canvas on slide 02 and the 01 <-> 02 moves (one continuous shot)
      if (window.siteloop?.handles?.(index, slide)) return;
      // S15: slide 01 = full-viewport canvas with the site context; elsewhere the
      // context fades out over 900 ms and the canvas returns to its grid box
      const title = index === 0;
      tower.setFull(title && mqSlides.matches);
      tower.setContext(title);
    });
    mqSlides.addEventListener('change', () => {
      const title = deck.index === 0;
      if (window.siteloop?.handles?.(deck.index, deck.slides[deck.index])) return;
      tower.setFull(title && mqSlides.matches);
      if (title) tower.setContext(true, 0);
    });
  } else {
    show(-1, true);
  }
  if (state.ctx.desired) loadContext();        // requested by the intro before the scene existed
  resolveReady();
}

main().catch((err) => {
  console.error(err);
  if (state.status !== 'fallback') fallback(`tower failed (${err.message})`);
});
