# Changelog

Format: one section per tag, newest first. Site releases use `vMAJOR.MINOR.PATCH`; documentation milestones use `plan-vX.Y`.

## plan-v1.3 — 2026-10-08

- Entry intro added as S13 Map Data (Opus high: OpenStreetMap download, geo-registration of the site model by OSM way ids, monochrome city and corridor SVGs), S14 Site GLB (Opus high: site context GLB from `02_Site/Arch575_BlenderSite_RhinoModel_v2.0.3dm`, tower placement) and S15 Intro Sequence (Fable: map zoom to Chicago scale, grey-out with the Randolph corridor in accent, zoom to the corridor, cross-fade to a top-down 3D view, descent to the title camera). Runs right after S7; the reviewer comments (S10–S12) now wait for S15.
- Site model moved from `Downloads\Site (1).3dm` to `02_Site\Arch575_BlenderSite_RhinoModel_v2.0.3dm` (168,187,546 bytes). Google 3D Tiles layer excluded from the website.
- Prompts regenerated against plan v1.3; new `S13_MapData.md`, `S14_SiteGLB.md`, `S15_IntroSequence.md`; S7 hands off to S13; S15's handoff is conditional (S10 or S8). Plan v1.2 copied to `docs/_superseded/`.

## Unreleased (v1.0.0 candidate, awaiting copy confirmation) — 2026-10-08

- Story slides (review T4): `data/story.json` (optional; without it the deck is the 12-slide build). Intro after the site slide: Thesis, Stacking (office 827,970 sf vs 812,500 sf target, 305 keys), Ground floor; outro after the levels: two massing views (greyscale copies of the 10/05 placeholders in `assets/story/`) and a closing slide repeating the title. Deck now 18 slides. New `tpl-text`, slide kinds `text` and `image` in `js/app.js`; tower shows on text slides (cols 7–12, no highlight), hidden on image slides.
- Projector legibility (T3): 13 px counter, data labels, key labels, scale-bar text and captions; labels and captions muted.
- Copy (T1, pending Brad): L16 "Transfer and booster pumps.", L33 "Transfer and booster pumps; rooftop-bound systems." via `MidReview_LevelDeck_v1.4.py`.
- Numbers (T2): plate and core re-checked against V14 v1.3 slab boundaries; unchanged.
- `tools/review_s6.py`: level slides found by kind; 390 px scroll-width check.

## v0.4.0 — 2026-10-08

- Plans re-rendered from `Core_Tower_V14_v1.3.3dm` (saved 2026-10-08 17:07; includes the Office 1 open plan, Office 2 executive floor, L34 clubhouse edits and the L17 fit-out) with `tools/Core_V13_PlanFurnished_v1.4.py --nogen L1,L2,V,W` (model furniture only on L06–L15, L17, L18–L32, L34; no duplicated generated furniture).
- v1.4 script: rooms on the office plans classed as Office (executive offices and suites were reading as Hotel/Amenity grey and adding Hotel to the office-floor key).
- `assets/plans/PlanColor_<key>_v1.4.svg` ×10 + `legend_v1.4.json`; `data/levels.json` and `tools/build_levels.py` point at v1.4 (new file names also bypass cached v1.3 SVGs). Legend keys per level unchanged. Plate/core table values not recomputed.

## plan-v1.2 — 2026-10-08

- Reviewer comments added as conditional subtasks S10 Comment API (Opus medium), S11 Phone Comments (Opus high), S12 Presenter Overlay (Fable): Cloudflare Worker + KV, phone comment/sketch layer, presenter overlay with a 13th Comments slide. Run only if `v1.0.0` is live by 22:00 and Brad supplies a Cloudflare API token (`_local/cf.env`, gitignored).
- Prompts regenerated against plan v1.2; new `docs/prompts/S10_CommentAPI.md`, `S11_PhoneComments.md`, `S12_PresenterOverlay.md`, `Brad_Cloudflare_Token.md`. S7's handoff is now conditional (S10 or S8).
- Tags `v1.1.0` / `v1.2.0` go to S8 and S10–S12 in the order they ship. Plan v1.1 copied to `docs/_superseded/`.

## v0.3.0 — 2026-10-08

- 3D tower (S5): `js/tower.js` loads `assets/tower.glb` once with three.js 0.186.1 through an importmap in `index.html` (`three` → `./js/vendor/three.module.js`, `three/addons/` → `./js/vendor/addons/`); transparent `WebGLRenderer`, `PerspectiveCamera` fov 28, hemisphere + camera-parented directional light; GLB materials replaced by flat neutral greys (accent stays the only hue).
- One accent `MeshStandardMaterial` box per level (plan box ± 0.5 in x/z, level y range, + 0.02 per face), only the active level visible; none on the title and site slides.
- Camera: yaw 31.95° + 36° × level index (title/site use index 0), pitch −7.74°; on `deck.on('change')` the yaw (shortest path) and the look-at height (toward the active level, clamped so the whole tower stays in frame) tween over 900 ms ease-in-out-cubic; instant under `prefers-reduced-motion`; render on demand only. Fit over all yaws with 6 % padding; `ResizeObserver` on `#tower-wrap`.
- Fallback: no WebGL or GLB failure → `assets/tower-fallback.png` (static render of slide 06) in the tower column plus a console warning; `#tower[hidden]` and `.deck__tower-fallback` rules in `css/app.css`.
- `window.tower` debug API (`ready`, `status`, `yaw`, `targetY`, `yawFor`, `levels[].bounds`, `active`, `distance`, `clamp`, `show`).

## v0.2.0 — 2026-10-08

- Page shell: `index.html` (running header with eyebrow + `nn / 12` counter, `<main class="deck">` with a persistent `<canvas id="tower">` wrapper, prev/next buttons, three `<template>`s), `css/app.css` (12-column grid, 72 px margins, text cols 1–3 / tower cols 4–6 / plan cols 7–12; title slide text cols 1–6 + tower cols 7–12; site image cols 1–8 + lines cols 9–12; < 900 px stacked scroll with the tower sticky at 40vh), `js/app.js` (renders 12 slides from `data/levels.json`, keys, buttons, swipe, hash `#01`…`#12`, fullscreen on `F`, reduced-motion, `IntersectionObserver` in scroll mode, `window.deck` API for `js/tower.js`).
- Plan figures: scale bar and north mark (north left) sized from the rendered plan (1 in = 40 ft → 2.4 px/ft × fit scale), caption `Fig. nn — Name, 1 in = 40 ft.`
- Plans v1.3 SVG (S3): `assets/plans/PlanColor_<key>_v1.3.svg` ×10 + `legend_v1.3.json` rendered by `Core_V13_PlanFurnished_v1.3.py` (oxide accent `#B0431F`, outdoor `#EFD9D2`, pool `#D7A18F`), mirrors in `tools/`.
- `data/levels.json` built by `tools/build_levels.py` from `MidReview_LevelDeck_v1.3.py` (10 levels, 8 programs, oxide accent `#B0431F`, legend keys from `legend_v1.2.json`).
- `assets/tower.glb` (11,108,308 bytes, copy of `TowerModel_GLB_v1.0.glb`), `assets/site.jpg` (1969×1170, JPEG q85).
- three.js **0.186.1** (r186) vendored by `tools/vendor_three.py` into `js/vendor/`: `three.module.js`, `three.core.js`, `addons/loaders/GLTFLoader.js`, `addons/utils/BufferGeometryUtils.js`, `addons/utils/SkeletonUtils.js`. No CDN at runtime.

## plan-v1.1 — 2026-10-08

- Review confirmed Fri 2026-10-09 09:00; v1.0.0 live target moved to Wed 2026-10-08 23:00 (hard limit Thu 07:30). S6–S7 run tonight.
- Added `docs/prompts/Brad_GoDaddy_CNAME.md` (Claude app walkthrough for the S1 gate).
- Plan v1.0 copied to `docs/_superseded/`.

## v0.1.0 — 2026-10-08

- Placeholder page live: `index.html` (eyebrow, title, two title lines, "Site in progress.", `noindex`), `404.html`, `CNAME` (`arch575.bradmachado.com`), `.nojekyll`.
- `css/style.css` vendored from `bradleymachado/bradleymachado.github.io` (main, 2026-10-08, 16,279 bytes); `css/app.css` created (header only).
- GitHub Pages enabled via API (branch `main`, root); custom domain set via API; `protected_domain_state: verified`. GoDaddy CNAME pending (Brad).

## plan-v1.0 — 2026-10-08

- Build plan v1.0, progress log v1.0, agent prompts S0–S9, reference handoffs (site handoff v1.0, subdomain handoff v1.0).
- Toolchain decided: GitHub Pages (public), static HTML/CSS/ES-module JS, three.js vendored, Python 3.10 build scripts.
