# Changelog

Format: one section per tag, newest first. Site releases use `vMAJOR.MINOR.PATCH`; documentation milestones use `plan-vX.Y`.

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
