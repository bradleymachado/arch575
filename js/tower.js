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
   ========================================================================== */

import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';

const GLB_URL = 'assets/tower.glb';
const DATA_URL = 'data/levels.json';
const FALLBACK_URL = 'assets/tower-fallback.png';

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
};

let resolveReady;
const ready = new Promise((res) => { resolveReady = res; });

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

  function place(cam, tgt, yawDeg, dist) {
    const az = yawDeg * DEG;
    const p = pitch * DEG;
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

  function render() {
    target.set(centre.x, state.targetY, centre.z);
    place(camera, target, state.yaw, state.distance);
    renderer.render(scene, camera);
  }

  function frame() {
    rafId = 0;
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
    if (anim) requestFrame();
  }

  function requestFrame() {
    if (!rafId) rafId = requestAnimationFrame(frame);
  }

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

  function resize() {
    const w = wrap.clientWidth;
    const h = wrap.clientHeight;
    if (!w || !h) return;
    renderer.setSize(w, h, false);
    camera.aspect = w / h;
    camera.updateProjectionMatrix();
    refit();
    if (!anim) state.targetY = targetYFor(state.active);
    requestFrame();
  }

  new ResizeObserver(resize).observe(wrap);
  resize();

  /* ---- deck ------------------------------------------------------------- */

  let first = true;
  state.status = 'ready';
  if (deck) {
    deck.on('change', (index, slide) => {
      show(slide.levelIndex, first);
      first = false;
    });
  } else {
    show(-1, true);
  }
  resolveReady();
}

main().catch((err) => {
  console.error(err);
  if (state.status !== 'fallback') fallback(`tower failed (${err.message})`);
});
