# arch575.bradmachado.com — Build Plan v1.0

2026-10-08 · ARCH 575, Fall 2026 · Brad Machado · Strategy conversation → chained agent subtasks S0–S9.
Companion: `docs/Arch575Site_ProgressLog_v1.0.md` (shared state; every subtask appends one entry).
Sources: `docs/reference/Arch575Site_Handoff_v1.0.md` (content, design direction) and `docs/reference/Subdomain_Handoff_v1.0.md` (DNS, Pages procedure, design system). Their rules govern.

## 0. Decisions taken in the strategy conversation

| ID | Decision | Result |
|---|---|---|
| Toolchain | Hosting and stack (Brad, 2026-10-08) | **GitHub Pages, public repo `bradleymachado/arch575`.** Static HTML + CSS + ES-module JS. three.js 0.186.1 vendored (no CDN at runtime). Python 3.10.11 build scripts. No Node, no build step. DNS stays at GoDaddy. Cloudflare Access was ruled out: it only evaluates requests on a hostname inside a Cloudflare zone, so a password would have required moving the bradmachado.com zone the day before the review. |
| D2 | Accent | `#B0431F` oxide red (main-site system). Tints: OUTDOOR `#EFD9D2` (20 % on white), POOL `#D7A18F` (50 %). |
| D3 | Plan source | v1.2 plans re-rendered as SVG from the saved `Core_Tower_V14_v1.2.3dm` now (S3). Re-render from `Core_Tower_V14_v1.3.3dm` with the L1/L2 generators off once Brad saves it (S8). |
| D4 | Page form | One `index.html`: full-viewport slides with keyboard navigation at ≥ 900 px; stacked scroll below 900 px. |
| D5 | Main-site link-in | Not before the review. S9 is listed but not scheduled; needs Brad's approval to push. |
| Catalogue | Where things live (Brad, 2026-10-08: "catalogued and stored on my GitHub with versioning") | The repo is the catalogue: `docs/` (plan, log, prompts, reference), `tools/` (build scripts), site files at root. Git tags mark releases. OneDrive `03_Design\05_Presentation\Web\` holds mirrored copies of plan and log plus the PROJECT_LOG entries. |

## 1. Fixed inputs and check values

| Item | Value |
|---|---|
| Review | Fri 2026-10-09. Time `[BRAD TO CONFIRM]`; the plan assumes 13:00. |
| Live target | v1.0.0 live by Thu 2026-10-09 09:00 (≥ 1 h before the earliest plausible review slot, with DNS margin). Placeholder live tonight so the HTTPS certificate issues overnight. |
| Live URL | `https://arch575.bradmachado.com` |
| Repo | `https://github.com/bradleymachado/arch575` · local `C:\Users\User\Projects\arch575` · branch `main` · Pages source: branch `main`, folder `/ (root)` |
| DNS record (Brad adds, after the custom domain is set on GitHub) | CNAME `arch575` → `bradleymachado.github.io`, default TTL. Never touch the apex A records, `www`, or `_github-pages-challenge-bradleymachado`. |
| Repo-name collision list | `arch575` is not on the main site's slug list. OK. |
| Backup deck | `<ROOT>\03_Design\05_Presentation\Tower_LevelDeck_v1.7.pptx` (keep) |
| `<ROOT>` | `C:\Users\User\OneDrive - University of Illinois - Urbana\Architecture\2026 Fall - Arch 575\` |
| Content source | `<ROOT>\05_Analysis_Tools\MidReview_LevelDeck_v1.3.py` → `LEVELS`, `PROG`, `KEY_ORDER`; boxes from `MidReview_LevelDeck_v1.2.py` |
| Plan renderer | `<ROOT>\05_Analysis_Tools\Core_V13_PlanFurnished_v1.2.py` (+ `Core_V13_PlanPrint_v1.2.py`), reads the .3dm with rhino3dm 8.35.0, matplotlib 3.10.9 |
| Model | `<ROOT>\03_Design\02_Circulation_Structure\Core_Tower_V14_v1.2.3dm` (saved 2026-10-05). v1.3 not yet saved. |
| GLB | `<ROOT>\03_Design\05_Presentation\Web\Assets\TowerModel_GLB_v1.0.glb`, 11,108,308 bytes, glTF units, y up |
| Highlight boxes (x0, x1, z0, z1), pad 0.5 | `F_OFF1 = (7.9, 97.8, 0.3, 39.9)` · `F_OFF2 = (27.7, 97.8, 0.3, 39.9)` · `F_HOT = (31.1, 72.5, 3.7, 36.6)` · `F_POD = (0.0, 97.8, 0.0, 63.4)` · `HOT_SPLIT = 163.4 + (219.5 − 163.4) × 7/13 = 193.6077` |
| Camera start (template) | yaw `ay = 1917107 / 60000 = 31.95°`, pitch `ax ≈ −7.74°`, roll `az ≈ −4.11°`; `ORBIT = 36°` per level (10 levels = one turn) |
| Plans (current) | `<ROOT>\03_Design\05_Presentation\MidReview\PlanFurnished_V14_v1.2\PlanColor_<key>_v1.2.png`, 450 dpi, 1 in = 40 ft, north left |
| Site image | `<ROOT>\03_Design\05_Presentation\TechReport1_Process\TR1_v2_cover_ssw.jpg` |
| Design tokens | Subdomain handoff §4, vendored `css/style.css` from `https://raw.githubusercontent.com/bradleymachado/bradleymachado.github.io/main/css/style.css` |
| Environment (verified 2026-10-08) | Python 3.10.11 · rhino3dm 8.35.0 · matplotlib 3.10.9 · Markdown 3.10.3 · numpy 2.2.6 · git · gh (logged in as `bradleymachado`) · Edge at `C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe` · **no Node** |

### Level data (check values; efficiency = (plate − core) / plate)

| # | key | label | name | sub | program | box | y0–y1 | rows |
|---|---|---|---|---|---|---|---|---|
| 01 | B1 | B1 | Basement | Plant | MEP | F_POD | −5.0–0.0 | Area 43,378 sf |
| 02 | L05 | L05 | Function | + Conference | AMENITY | F_OFF1 | 17.5–23.2 | Area 35,143 sf |
| 03 | L06-L15 | L06–15 | Office 1 | Typical | OFFICE | F_OFF1 | 23.8–77.9 | Floors 10 · Plate 39,930 sf · Core 6,386 sf · Efficiency 84.0 % |
| 04 | L16 | L16 | Mechanical 1 | | MEP | F_OFF1 | 77.9–80.4 | Area 39,930 sf |
| 05 | L17 | L17 | Holodeck | | AMENITY | F_OFF1 | 80.4–82.8 | Area 25,203 sf |
| 06 | L18-L32 | L18–32 | Office 2 | Executive | OFFICE | F_OFF2 | 83.4–158.5 | Floors 15 · Plate 28,578 sf · Core 4,466 sf · Efficiency 84.4 % |
| 07 | L33 | L33 | Mechanical 2 | | MEP | F_OFF2 | 158.5–161.0 | Area 28,578 sf |
| 08 | L34 | L34 | Hotel Clubhouse | + Pool | AMENITY | F_OFF2 | 161.0–163.4 | Area 11,760 sf |
| 09 | L35-L41 | L35–41 | Hotel A | | HOTEL | F_HOT | 164.0–193.6077 | Floors 7 · Keys 23 · Plate 14,040 sf · Core 2,480 sf · Efficiency 82.3 % |
| 10 | L42-L47 | L42–47 | Hotel B | | HOTEL | F_HOT | 193.6077–219.5 | Floors 6 · Keys 24 · Plate 14,040 sf · Core 2,480 sf · Efficiency 82.3 % |

Descriptions (Claude-drafted, **Brad must confirm**): see `LEVELS` in the deck script and handoff §3. Title: "West Loop Gateway · Mixed-use tower, 735 W. Randolph St. · ARCH 575 mid-review, Fall 2026". Site: "735 W. Randolph St. · West Loop, Chicago · Randolph to Washington. Kennedy Expressway to the east. Gateway to Restaurant Row."

Program key (label, colour): OFFICE Office `#B5B5B5` · HOTEL Hotel `#B5B5B5` · AMENITY Amenity `#B5B5B5` · OUTDOOR Outdoor `#EFD9D2` · CIRCULATION Circulation `#FFFFFF` · NOSTOP Elevator, no stop `#F0F0F0` · BOH Back of house `#D9D9D9` · MEP MEP `#3A3A3A`. The level's own program takes the accent in the key, the plan, and the tower box.

## 2. Repository layout, versioning, catalogue rules

```
arch575/
  index.html  404.html  CNAME  .nojekyll  README.md  CHANGELOG.md  .gitignore
  css/style.css (vendored, never edited)   css/app.css
  js/app.js  js/tower.js
  js/vendor/three.module.js  js/vendor/addons/loaders/GLTFLoader.js  js/vendor/addons/utils/BufferGeometryUtils.js
  data/levels.json
  assets/tower.glb  assets/site.jpg  assets/tower-fallback.png  assets/plans/PlanColor_<key>_v1.3.svg
  tools/build_levels.py  tools/vendor_three.py
  tools/Core_V13_PlanFurnished_v1.3.py (mirror)  tools/Core_V13_PlanPrint_v1.2.py (mirror)
  docs/Arch575Site_Plan_v1.0.md  docs/Arch575Site_ProgressLog_v1.0.md  docs/prompts/S0..S9.md
  docs/reference/*.md  docs/_superseded/
```

- **Branch:** `main` only; every push to `main` deploys. Solo project; no PRs required.
- **Commits:** `section: what changed` (`docs:`, `scaffold:`, `data:`, `plans:`, `shell:`, `tower:`, `review:`, `deploy:`). One commit per subtask minimum. End the message with `Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>`.
- **Release tags (annotated):** `v0.1.0` placeholder live · `v0.2.0` data + plans + shell · `v0.3.0` 3D tower · `v1.0.0` review build (after S6 pass and copy confirmed) · `v1.1.0` plans from V14 v1.3 · `plan-v1.0` on the docs commit. `CHANGELOG.md` gets a section per tag.
- **Plan revisions:** v1.1, v1.2 … Copy the previous file to `docs/_superseded/` (never delete), update `CHANGELOG.md`, add a one-line log entry, mirror to OneDrive `Web\`.
- **Scripts:** anything that reads the `.3dm` is canonical in `<ROOT>\05_Analysis_Tools` (CLAUDE.md) and mirrored to `tools/` at the version used. Site-only scripts are canonical in `tools/`.
- **Never delete** in the repo or OneDrive; supersede. Never commit a `.3dm`. `.gitignore`: `__pycache__/`, `*.pyc`, `.DS_Store`, `Thumbs.db`, `*.3dm*`, `_local/`.
- **Mirror to OneDrive at every tag:** plan + log to `<ROOT>\03_Design\05_Presentation\Web\`; one PROJECT_LOG entry per session at the top with full absolute paths.

## 3. Rules for every agent

1. Read this plan and the log first. Execute only your subtask. Do not re-plan.
2. Never save a `.3dm`. Scripts read the model only. Never touch `C:\Users\User\Projects\bradmachado-com`, the main repo, or any existing DNS record.
3. No invented copy. Unknowns go in `[BRACKETS]` and into the log's "For Brad" list.
4. Preview with `python -m http.server 8000` from the repo root (module scripts and the GLB fail from `file://`). Captures use **headless Edge** (`"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe" --headless=new --screenshot=<png> --window-size=1920,1080 <url>`), which is not GUI automation. No Chrome or computer-use automation while Brad is at the machine.
5. Accent and tokens only from §0/§1. No second hue, no shadows, no rounded corners, no gradients, no callouts or arrows on plans.
6. Answers to Brad: lead with the result, number the steps, literal click paths, one question at a time. Gated subtasks end with `STOP - report <value> before I continue.` and nothing after it.
7. On completion: commit, append the log entry (template in the log), capture ≥ 1 environment image and ≥ 1 clean output image to `<ROOT>\03_Design\05_Presentation\Web\Process\Arch575Site_S<N>_<Desc>_v1.0.png`, then output the next subtask's prompt from `docs/prompts/` with placeholders replaced, as the last fenced block.

## 4. Subtasks

Order: S0 → S1 (gate: GoDaddy CNAME) → S2 ∥ S3 → S4 → S5 → S6 → S7 → S8 (after Brad saves V14 v1.3) → S9 (post-review, optional).
Model tiers are the `cs-exec-*` agent types: `lite` = Sonnet, `medium` = Opus medium, `high` = Opus high, `top` = Fable high.

### S0 · Env Check · 10 min · `cs-exec-lite`
Inputs: §1 environment row.
Steps: (1) `python --version`; `python -c "import rhino3dm, matplotlib, markdown, pptx; print('ok')"`; `git --version`; `gh auth status`. (2) `gh repo view bradleymachado/arch575` and `nslookup arch575.bradmachado.com` (expect no record yet). (3) Inspect the GLB with Python (`struct` + `json` on the GLB header): print node count, mesh count, overall min/max of the POSITION accessors; confirm y is up (max y ≈ 220, x ≈ 0–98, z ≈ 0–63). (4) Confirm Edge headless works: screenshot `https://bradmachado.com` to the scratchpad at 1920×1080. (5) Log entry.
Outputs: log entry with the printed values. Acceptance: all four imports OK; GLB extents consistent with the boxes in §1; headless screenshot exists.
Gate: STOP only if an import fails or the GLB extents disagree with §1.

### S1 · Repo Scaffold · 20 min · `cs-exec-medium`
Inputs: §2 layout, subdomain handoff §3 and §5, tokens §4.
Steps: (1) In `C:\Users\User\Projects\arch575` (already a git repo with `docs/`): add `CNAME` (`arch575.bradmachado.com`, one line), empty `.nojekyll`, `404.html` (handoff §5 pattern, `noindex`, absolute links), vendored `css/style.css` from the raw GitHub URL, `css/app.css` (header comment only), placeholder `index.html` on the handoff §5 skeleton: header, eyebrow `ARCH 575 / Mid-review`, title "West Loop Gateway", the two §1 title lines, line "Site in progress.", plus `<meta name="robots" content="noindex">`. (2) Commit `scaffold: placeholder page, CNAME, 404`; `git push -u origin main`. (3) Enable Pages and set the custom domain through the API, in this order: `gh api -X POST repos/bradleymachado/arch575/pages -f build_type=legacy -f "source[branch]=main" -f "source[path]=/"` then `gh api -X PUT repos/bradleymachado/arch575/pages -f cname=arch575.bradmachado.com`. If either call fails, give Brad the click path from subdomain handoff §3 steps 3–4 and stop. (4) `gh api repos/bradleymachado/arch575/pages` must show `cname: arch575.bradmachado.com`. Tag `v0.1.0`; `CHANGELOG.md` entry. (5) Give Brad the GoDaddy step verbatim from subdomain handoff §3 step 5.
Outputs: pushed repo, Pages enabled, custom domain set, tag. Acceptance: API shows the cname; `https://bradleymachado.github.io/arch575/` responds (may redirect).
Gate: `STOP - report when the GoDaddy CNAME arch575 -> bradleymachado.github.io is saved before I continue.` (S2 and S3 may start in parallel; only S7 needs the DNS result.)

### S2 · Data Assets · 15 min · `cs-exec-medium`
Inputs: §1 content source, GLB, site image, three.js 0.186.1.
Steps: (1) Write `tools/build_levels.py`: load `MidReview_LevelDeck_v1.3.py` via `importlib` (it imports v1.2 and python-pptx), emit `data/levels.json` with `title`, `site`, `accent`, `orbitDeg`, `camera {azDeg, pitchDeg, rollDeg}`, `programs` (from `PROG` with the §1 colours, in `KEY_ORDER`), `levels[]` with `key, label, name, sub, description, rows, program, box [x0,x1,z0,z1], y [y0,y1], keys` (from `legend_v1.2.json`, ordered by `KEY_ORDER`), `plan` path `assets/plans/PlanColor_<key>_v1.3.svg`. (2) Copy the GLB to `assets/tower.glb` and the site image to `assets/site.jpg` (resize to ≤ 2400 px long edge, JPEG q85, with Pillow if present, else copy). (3) Write `tools/vendor_three.py`: download `https://cdn.jsdelivr.net/npm/three@0.186.1/build/three.module.js`, `.../examples/jsm/loaders/GLTFLoader.js`, `.../examples/jsm/utils/BufferGeometryUtils.js` into `js/vendor/` per §2; record the version in `CHANGELOG.md`. (4) Validate: 10 levels, every `rows` string matches §1, `HOT_SPLIT` = 193.6077, 8 programs. (5) Commit `data: levels.json, tower.glb, site.jpg, three 0.186.1`; log entry with the **13 copy lines for Brad to confirm** (title, site, 10 descriptions, plus the name "Holodeck").
Outputs: `data/levels.json`, `assets/tower.glb`, `assets/site.jpg`, `js/vendor/*`. Acceptance: the four checks in step 4; `tower.glb` byte count 11,108,308.

### S3 · Plan SVG · 25 min · `cs-exec-high`
Inputs: renderer v1.2, PlanPrint v1.2, model v1.2, §0 D2 colours.
Steps: (1) Copy to `<ROOT>\05_Analysis_Tools\Core_V13_PlanFurnished_v1.3.py`. Changes: `ACCENT = "#B0431F"`, `COL["OUTDOOR"] = "#EFD9D2"`, `POOL = "#D7A18F"`; CLI flags `--fmt svg|png` (default svg), `--accent HEX`, `--nogen L1,L2` (skip the generated furniture for the listed plan prefixes; the model's ExecOffice/OpenOffice objects then carry the furniture); output names `PlanColor_<key>_v1.3.<fmt>` and `legend_v1.3.json`; SVG via `savefig(format="svg")`; keep the elevator no-stop rule. (2) Run against `Core_Tower_V14_v1.2.3dm` **without** `--nogen` (that model predates the ExecOffice/OpenOffice objects) into `<ROOT>\03_Design\05_Presentation\MidReview\PlanFurnished_V14_v1.3\`. (3) Report file sizes; if any SVG > 3 MB, re-run that level with `--fmt png` at 300 dpi and note it. (4) Copy the plans to `assets/plans/` and the script plus PlanPrint to `tools/`; update `plan` paths in `levels.json` if PNG was used. (5) Commit `plans: v1.3 SVG, oxide accent`; log entry.
Outputs: 10 plan files, `legend_v1.3.json`, script v1.3. Acceptance: 10 files; legend keys equal `legend_v1.2.json`; no navy (`#1F3A5F`, `#D3DAE3`, `#A9B7C9`, case-insensitive) in any SVG; each SVG renders in Edge headless without error.

### S4 · Page Shell · 30 min · `cs-exec-high`
Inputs: `levels.json`, plans, tokens, handoff §2 design direction.
Steps: (1) `index.html`: skeleton from subdomain handoff §5 with `<main>` holding 12 `<section class="slide">` (title, site, 10 levels) rendered by `js/app.js` from `levels.json` (fetch) into a `<template>`; running header: left `ARCH 575 / West Loop Gateway` eyebrow, right `02 / 12` mono, 1 px hairline below; bottom-right prev/next buttons. (2) `css/app.css`, desktop ≥ 900 px: each slide = 100 vh, 12-column grid, 72 px margins; cols 1–3: level label (Helvetica, ~160 px, tracking −0.03 em), name 28 px ink, sub 28 px muted, description 15 px body, ruled data table (mono 11 px uppercase labels, hairlines), vertical key (12 px squares, 1 px hairline border on white and pale swatches, accent first); cols 4–6: `#tower` canvas full height; cols 7–12: plan `<img>` fitted with `object-fit: contain`, scale bar and north arrow (north left) as a small inline SVG under the plan, caption in the `Fig. 0n — <name>, 1 in = 40 ft.` style. Title slide: eyebrow, h1, two lines. Site slide: image cols 1–8, three lines cols 9–12. Below 900 px: slides stack at natural height, 24 px margins, tower canvas `position: sticky; top: 0; height: 40vh`, plan below text. (3) `js/app.js`: slide state, keys (← → Space PageUp PageDown Home End), `F` toggles fullscreen, click/tap arrows, swipe, URL hash `#01` … `#12` (deep-link and back button), `prefers-reduced-motion` respected; expose `window.deck.on('change', i => …)` for S5; on phone, `IntersectionObserver` sets the active level. (4) Preview on `http://localhost:8000`; headless-Edge captures at 1920×1080 and 390×844 for slides 01, 03 and 06. (5) Commit `shell: slides, grid, navigation`; tag `v0.2.0`; log entry.
Outputs: `index.html`, `css/app.css`, `js/app.js`, captures. Acceptance: 12 slides; every number on screen equals §1; no text other than `levels.json` content and labels; no horizontal scroll at 390 px; hash navigation works.

### S5 · 3D Tower · 30 min · `cs-exec-top`
Inputs: `assets/tower.glb`, `levels.json` boxes/y/camera, vendored three.js.
Steps: (1) `js/tower.js` as an ES module with an importmap in `index.html` (`"three": "./js/vendor/three.module.js"`, `"three/addons/": "./js/vendor/addons/"`): transparent `WebGLRenderer` (alpha, `setPixelRatio(Math.min(devicePixelRatio, 2))`), `PerspectiveCamera` fov 28, `HemisphereLight` + one `DirectionalLight`, load the GLB once with `GLTFLoader`; keep the model's materials; centre on the bounding box; fit the whole tower in the canvas height with 6 % padding. (2) One `Mesh(BoxGeometry)` per level from `box` + pad 0.5 and `y`, `MeshStandardMaterial({color: accent, roughness: 0.9})`, only the active one visible; offset 0.02 outside the facade on each side to avoid z-fighting. (3) Camera: yaw = 31.95° + 36° × index (title and site slides use index 0), pitch −7.74°, roll ignored; on `deck.on('change')` tween yaw and the look-at height (toward the centre of the active level's `y`, clamped so the whole tower stays in frame) over 900 ms ease-in-out-cubic; no continuous spin; render on demand (`requestAnimationFrame` only while tweening or resizing). (4) Fallback: if WebGL is unavailable or the GLB fails, show `assets/tower-fallback.png` (a headless-Edge capture of the loaded tower at slide 06, cropped, saved by this subtask) and log a console warning. (5) Preview; captures at slides 01, 03, 06, 10; commit `tower: GLB, level highlight, camera tween`; tag `v0.3.0`; log entry.
Outputs: `js/tower.js`, importmap, `assets/tower-fallback.png`, captures. Acceptance: first paint < 3 s on localhost; yaw differs by exactly 36° between consecutive levels (log the values); highlight box bounds equal §1 boxes ± pad; no console errors; works with `python -m http.server` offline (no network requests other than Google Fonts, which may fail silently).

### S6 · Review · 20 min · `cs-exec-high`
Inputs: handoff §2 and §9, subdomain handoff §4 and §9, §1 of this plan, captures.
Steps: (1) Pass/fail table against handoff §9 "Done means" and subdomain §9, plus: tokens only, accent is the only hue, flush-left type, no callouts or arrows, plans grey with one accent program, hotel elevators never read as office circulation on L18–32 (NOSTOP symbol present), no `[BRACKETS]` left on screen. (2) Numbers: every rendered number diffed against §1 by script (load `levels.json`, compare to a literal copy of §1 in the review script). (3) Headless-Edge captures of all 12 slides at 1920×1080 and 390×844 into `<ROOT>\03_Design\05_Presentation\Web\Process\`; view each capture and note defects. (4) Copy status: list which of the 13 copy lines Brad has confirmed (from the log); unconfirmed lines block `v1.0.0`. (5) Fix defects that are one-line CSS/JS changes; log everything else as "For S7 / For Brad". Commit `review: fixes`; log entry.
Outputs: review table in the log, captures. Acceptance: all rows pass or are assigned.
Gate: `STOP - report confirmation of the copy lines listed, or your edits, before I continue.`

### S7 · Deploy Log · 15 min · `cs-exec-medium`
Inputs: S6 result, DNS result from S1's gate.
Steps: (1) Apply Brad's copy edits to `levels.json` (and to `LEVELS` in the deck script as `MidReview_LevelDeck_v1.4.py` if wording changed, so deck and site agree); commit `deploy: confirmed copy`. (2) `nslookup arch575.bradmachado.com` → `bradleymachado.github.io` and 185.199.108–111.153; `gh api repos/bradleymachado/arch575/pages` → `https_enforced`; if false and the DNS check is green, `gh api -X PUT repos/bradleymachado/arch575/pages -F https_enforced=true`. (3) Push; tag `v1.0.0`; `CHANGELOG.md`. (4) Verify: `curl -I https://arch575.bradmachado.com` 200; headless capture of the live URL; `curl -I https://bradmachado.com` and `https://www.bradmachado.com` 200 and unchanged title. (5) Mirror plan + log to `<ROOT>\03_Design\05_Presentation\Web\`; PROJECT_LOG entry at the top with full paths; remind Brad of the offline run: `cd C:\Users\User\Projects\arch575` then `python -m http.server 8000`, open `http://localhost:8000`, press `F`.
Outputs: live site, tag, logs. Acceptance: handoff §9 all ticked except plans-from-v1.3 (S8).

### S8 · Plans v1.3 Model · 20 min · `cs-exec-high` · after Brad saves `Core_Tower_V14_v1.3.3dm`
Steps: (1) Confirm the file exists and its timestamp. (2) Run `Core_V13_PlanFurnished_v1.3.py` with `--nogen L1,L2` into `PlanFurnished_V14_v1.3b\` (bump the script to v1.4 if a change is needed, e.g. removing the lobby cut from handoff §6 item 3 once the model wall is fixed). (3) Diff legend keys against v1.3; visual check of the two office SVGs for duplicate furniture; check the L34 clubhouse opening and pool deck are present. (4) Copy to `assets/plans/`, commit `plans: from V14 v1.3, generators off`; tag `v1.1.0`; log and PROJECT_LOG entries. (5) Re-measure areas if the model changed plates; any change to §1 numbers is a plan revision (v1.1) and a deck update.
Gate: `STOP - report any plate or core number that changed before I continue.`

### S9 · Main-site Link-in · 15 min · `cs-exec-medium` · post-review, only on Brad's instruction
Per subdomain handoff §6: section `04 / Development`, row `D.01`, in a clone of the main repo; one commit; Brad approves before push. Not scheduled.

## 5. Schedule (Wed 2026-10-08 evening → Thu 2026-10-09 morning)

| Block | Subtasks | Minutes | With 20 % buffer | Cumulative |
|---|---|---|---|---|
| Tonight 1 | S0, S1 (+ Brad: GoDaddy CNAME, 2 min) | 30 | 36 | 0:36 |
| Tonight 2 | S2 ∥ S3 | 25 (parallel) | 30 | 1:06 |
| Tonight 3 | S4, S5 | 60 | 72 | 2:18 |
| Overnight | DNS propagation, certificate issue, Brad confirms copy | — | — | — |
| Thu AM | S6, S7 | 35 | 42 | 3:00 |
| Target | `v1.0.0` live by **Thu 2026-10-09 09:00** | | | |
| Later | S8 (after model save), S9 (post-review) | 35 | | |

Fallback at any point: present from `Tower_LevelDeck_v1.7.pptx`, or from the local folder with `python -m http.server`.

## 6. Tooling audit

| Need | Status |
|---|---|
| Python 3.10 + rhino3dm + matplotlib + python-pptx + Markdown | present |
| git, gh (auth OK) | present |
| three.js 0.186.1 (vendored; `GLTFLoader` imports `BufferGeometryUtils`) | S2 downloads |
| Node, wrangler | absent, not needed |
| Pillow (site image resize) | optional; S2 falls back to copy |
| Edge headless (captures, PDF) | present |
| Chrome automation / computer use | not used (CLAUDE.md) |
| Deprecated | PowerPoint Morph with per-slide GLB swap → replaced by the three.js tween. `KHR_materials_pbrSpecularGlossiness` in the deck's box builder is a deprecated glTF extension; the web box uses a plain `MeshStandardMaterial`. |
| Model tiers | S0 lite · S1 S2 S7 S9 medium · S3 S4 S6 S8 high · S5 top |

## 7. For Brad (open items)

1. Review time on Fri 2026-10-09 `[BRAD TO CONFIRM]`.
2. GoDaddy CNAME `arch575` after S1 reports the custom domain is set (S1 gate).
3. Confirm or edit the 13 copy lines S2 lists in the log (title, site, 10 descriptions, "Holodeck").
4. Save `Core_Tower_V14_v1.3.3dm` when today's Rhino work is done (triggers S8).
5. Pink area on Office 2 (service car SV-4 + lobby) drawn as back of house: confirm.
