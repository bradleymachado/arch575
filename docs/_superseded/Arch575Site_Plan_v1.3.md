# arch575.bradmachado.com — Build Plan v1.3

v1.3 2026-10-08 (entry intro S13–S15: Chicago map zoom, Randolph corridor, site-model descent; S16 site-access layer; review notes v1.1 folded in; deck is 18 slides) · v1.2 2026-10-08 (reviewer comments S10–S12, conditional) · v1.1 2026-10-08 (review time confirmed 09:00; live target moved to tonight) · v1.0 2026-10-08 · ARCH 575, Fall 2026 · Brad Machado · Strategy conversation → chained agent subtasks S0–S16.
Companion: `docs/Arch575Site_ProgressLog_v1.0.md` (log keeps v1.0; only the plan was revised) (shared state; every subtask appends one entry).
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
| D6 | Reviewer comments (Brad, 2026-10-08: "add this in at the end if we have time") | Reviewers comment and sketch on the slides from their phones; Brad clicks through the comments at the end. Three conditional subtasks S10–S12: Cloudflare Worker + KV comment API, phone comment/sketch layer, presenter overlay with a 13th "Comments" slide. **Run only if S15 (entry intro) is accepted by 22:00 tonight and Brad has supplied a Cloudflare API token** (§7 item 6). Inert without a query parameter, so partial work can stay on `main`. Reviewer names are free text (default; a fixed list was the alternative). |
| D7 | Entry intro (Brad, 2026-10-08: "google earth zoom … stop at Chicago scale and grey out everything else … show Randolph from the Loop all the way to our larger site model … open the Blender model starting at Chicago scale and zoom down to our Blender site model") | Slide 01 opens with a 12–14 s sequence: monochrome vector map zooming to Chicago scale, hold, grey-out with the Randolph corridor (Michigan Ave → the site model) in accent, zoom to the corridor, cross-fade to a top-down three.js view of the site model at the same framing, descent to the title camera with the tower standing on the site. Map data from OpenStreetMap with an attribution line, not Google Earth (no Google products; imagery licence). Site context from Brad's Blender site model via its Rhino export `02_Site\Arch575_BlenderSite_RhinoModel_v2.0.3dm` (moved from `Downloads\Site (1).3dm` on 2026-10-08); its hidden `Earth` layer (Google 3D Tiles) is excluded. Subtasks S13–S15 run right after S7 and before the reviewer comments; S16 adds the site-access layer (review notes T9) as a slide and a ground decal. Alternative if Brad wants photographic imagery for the zoom: USGS NAIP (public domain) or Google Earth frames with `Imagery © Google` (as the T5 views); say so before S13 runs. |
| D8 | Review notes v1.1 (other conversation, `docs/Arch575Site_ReviewNotes_v1.1.md`) | Folded in: T1–T4, T7 done by the S7 session (deck is 18 slides from `data/story.json`; copy gate now 18 rows; `v1.0.0` untagged until Brad confirms); S8 done (`v0.4.0`, plans v1.4); T9 = S13–S16 of this plan (live three.js context instead of Blender renders; C3 = S16); T6, T8 default no change; T5 (interior views over Google Earth) stays outside this plan, it needs the Rhino MCP conversation. Rule change (Brad, 2026-10-08): Rhino models are saved through the Rhino MCP `save_doc` as the next minor version, never over an earlier file; "never save a .3dm" is void. |

## 1. Fixed inputs and check values

| Item | Value |
|---|---|
| Review | **Fri 2026-10-09 09:00** (Brad, 2026-10-08). |
| Live target | **v1.0.0 live tonight, Wed 2026-10-08 by 23:00**; hard limit Thu 2026-10-09 07:30. The GoDaddy CNAME goes in as soon as S1 reports, so DNS and the HTTPS certificate settle while S2–S5 run. |
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
| Comment API (S10) | Cloudflare Worker `arch575-comments` at `https://arch575-comments.<subdomain>.workers.dev`, KV namespace `arch575_comments`, binding `COMMENTS`. Routes `GET` / `POST /c/<room>`. Room code: 6 chars `[a-z0-9]`, generated by S10, stored in `data/review.json`. CORS origins: `https://arch575.bradmachado.com`, `http://localhost:8000`. Limits: name 40, text 500, strokes ≤ 20,000 bytes, 200 comments per room. |
| Review URLs | Reviewer: `https://arch575.bradmachado.com/?review=<room>` (QR on the title slide in present mode). Presenter: `https://arch575.bradmachado.com/?present=<room>#01`. The plain URL is always the `v1.0.0` behaviour. |
| Cut-off | S13 starts now (S7 is done except the copy gate; every push deploys). S16 is skipped if it would start after **21:30**. S10 starts only if S16 is done or skipped by **22:00**; S12 accepted by **23:30**. `v1.0.0` is tagged by whichever subtask is running when Brad confirms the copy. At any cut-off Brad presents from the plain URL. |
| Deck state (2026-10-08 17:45) | 18 slides: title, site, 3 story text slides (Thesis, Stacking, Ground floor), 10 levels, 2 massing images, closing; `data/story.json`; slide kinds `title | site | text | image | level`; counter `nn / 18`. Level slides start at 06 (L18–32 = slide 11). Plans v1.4 (S8). |
| Site-access diagram (S16) | `<ROOT>\02_Site\Diagrams\735WRandolph_SiteAccess_Diagram_v1.0.pdf` (2,972,109 bytes; vector, 1,326 paths + 2 images). PyMuPDF 1.28 (`fitz`) present. Blender source of the site model: `<ROOT>\Downloads\Arch575_BlenderSite1.blend` (2026-09-25, not used by this plan). |
| Secrets | `_local/cf.env` (gitignored): `CF_ACCOUNT_ID=…`, `CF_API_TOKEN=…` (token scopes: Account · Workers Scripts · Edit, Account · Workers KV Storage · Edit). Never committed, never printed in a log or capture. |
| Site model (S13–S15) | `<ROOT>\02_Site\Arch575_BlenderSite_RhinoModel_v2.0.3dm` (168,187,546 bytes; Rhino 8 Educational, feet, created 2026-08-27; moved from `Downloads\Site (1).3dm` on 2026-10-08; **read only**). 2,728 objects, 30 layers. Use: `buildings` 172 extrusions named with OSM way ids (x 146–2381, y 227–2002, z −5–485 ft), `TERRAIN_MESH` 1 mesh (x −271–2796, y −168–2423), `Bridges` 901 meshes, `Roads` 1 brep (hidden), `Site` 1 polycurve (x 1331.7–1532.7, y 989.1–1327.4: the 201 × 338 ft L-site). Exclude: `Earth` (231 meshes named "Google 3D Tiles", hidden), all `Setup::*`, `TPX_TERRAIN`, `Rail`. No earth anchor: geo-registration comes from the OSM ids (S13). Render meshes exist on all 504 breps. |
| Tower ↔ site | Tower GLB is in metres (x 0–97.84 = 321 ft, z 0–63.40 = 208 ft, y 0–219.46 = 720 ft); the site model is in feet. Placement = fit of the F_POD footprint onto the `Site` polycurve's rectangle (GLB x runs N–S), cross-checked against the podium outline in `03_Design\00_Master\Randolph_Master_v1.1.3dm` (read only). S14 writes `towerOffset` and `towerYawDeg` into `data/site.json`. |
| Map data | OpenStreetMap via Overpass (`https://overpass-api.de/api/interpreter`, mirror `https://overpass.kumi.systems/api/interpreter`): city bbox lat 41.62–42.05, lon −87.98 … −87.50; corridor bbox lat 41.878–41.892, lon −87.662 … −87.618. Web Mercator, metres. Attribution `Map data © OpenStreetMap contributors`, mono 11 px, on the map stages. |
| Intro timing | A city zoom 2.5 s · hold 1.0 s · B grey-out + corridor draw 1.0 s · C corridor zoom 2.5 s · hold 1.5 s · D cross-fade 0.8 s + descent 3.0 s · title text 0.5 s ≈ 12.8 s. Skip: any key or click. `prefers-reduced-motion`: final frame only. `I` replays. |

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
  js/review.js  css/review.css  data/review.json  assets/qr-review.svg      (S10–S12; loaded only with ?review= or ?present=)
  worker/comments.js  tools/cf_deploy.py  tools/make_qr.py  _local/cf.env (gitignored, Brad's token)
  js/intro.js  css/intro.css  data/site.json  assets/map-city.svg  assets/map-corridor.svg  assets/site.glb   (S13–S15)
  tools/fetch_osm.py  tools/render_map.py  tools/build_site_glb.py  tools/decimate_blender.py (optional)   _local/osm_*.json (cache)
  assets/map-access.svg  assets/access-decal.png  tools/extract_access.py   (S16)   docs/Arch575Site_ReviewNotes_v1.1.md (review conversation)
  docs/Arch575Site_Plan_v1.2.md  docs/Arch575Site_ProgressLog_v1.0.md  docs/prompts/S0..S15.md  docs/prompts/Brad_*.md
  docs/reference/*.md  docs/_superseded/
```

- **Branch:** `main` only; every push to `main` deploys. Solo project; no PRs required.
- **Commits:** `section: what changed` (`docs:`, `scaffold:`, `data:`, `plans:`, `shell:`, `tower:`, `review:`, `deploy:`, `review-api:`, `review-ui:`, `review-overlay:`, `map:`, `site:`, `intro:`). One commit per subtask minimum. End the message with `Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>`.
- **Release tags (annotated):** `v0.1.0` placeholder live · `v0.2.0` data + plans + shell · `v0.3.0` 3D tower · `v1.0.0` review build (after S6 pass and copy confirmed) · `v0.4.0` plans v1.4 (S8, done) · builds before Brad confirms the copy keep tagging `v0.x` · `v1.0.0` = the first build after the copy is confirmed · later features (S15 intro, S16 access layer, S10–S12 comments) take the next minor in the order they ship · `plan-vX.Y` on each plan revision. `CHANGELOG.md` gets a section per tag.
- **Plan revisions:** v1.1, v1.2 … Copy the previous file to `docs/_superseded/` (never delete), update `CHANGELOG.md`, add a one-line log entry, mirror to OneDrive `Web\`.
- **Scripts:** anything that reads the `.3dm` is canonical in `<ROOT>\05_Analysis_Tools` (CLAUDE.md) and mirrored to `tools/` at the version used. Site-only scripts are canonical in `tools/`.
- **Never delete** in the repo or OneDrive; supersede. Never commit a `.3dm`. `.gitignore`: `__pycache__/`, `*.pyc`, `.DS_Store`, `Thumbs.db`, `*.3dm*`, `_local/`.
- **Mirror to OneDrive at every tag:** plan + log to `<ROOT>\03_Design\05_Presentation\Web\`; one PROJECT_LOG entry per session at the top with full absolute paths.

## 3. Rules for every agent

1. Read this plan and the log first. Execute only your subtask. Do not re-plan.
2. Rhino models are saved only through the Rhino MCP `save_doc` as the next minor version, never over an earlier file (Brad, 2026-10-08; replaces "never save a .3dm"). The scripts in this plan read `.3dm` files with rhino3dm only. Never touch `C:\Users\User\Projects\bradmachado-com`, the main repo, or any existing DNS record. Never commit `_local/cf.env`; never print the Cloudflare token into a log entry or a capture. The site model and the master model are read with rhino3dm; nothing in this plan writes them. Never open Blender or Rhino as a GUI from an agent; Blender only as `blender -b`.
3. No invented copy. Unknowns go in `[BRACKETS]` and into the log's "For Brad" list.
4. Preview with `python -m http.server 8000` from the repo root (module scripts and the GLB fail from `file://`). Captures use **headless Edge** (`"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe" --headless=new --screenshot=<png> --window-size=1920,1080 <url>`), which is not GUI automation. No Chrome or computer-use automation while Brad is at the machine.
5. Accent and tokens only from §0/§1. No second hue, no shadows, no rounded corners, no gradients, no callouts or arrows on plans.
6. Answers to Brad: lead with the result, number the steps, literal click paths, one question at a time. Gated subtasks end with `STOP - report <value> before I continue.` and nothing after it.
7. On completion: commit, append the log entry (template in the log), capture ≥ 1 environment image and ≥ 1 clean output image to `<ROOT>\03_Design\05_Presentation\Web\Process\Arch575Site_S<N>_<Desc>_v1.0.png`, then output the next subtask's prompt from `docs/prompts/` with placeholders replaced, as the last fenced block.

## 4. Subtasks

Order: S0 → S1 (gate: GoDaddy CNAME) → S2 ∥ S3 → S4 → S5 → S6 ✓ → S7 (done except the copy gate) → S13 → S14 → S15 → S16 (skipped if it would start after 21:30) → [S10 → S11 → S12, only if S16 is done or skipped by 22:00 and `_local/cf.env` exists] → closeout. S8 ✓ done (`v0.4.0`). S9 post-review, only on Brad's instruction. `v1.0.0` is tagged by whichever subtask is running when Brad confirms the copy.
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
Handoff: S13.

### S13 · Map Data · 25 min · `cs-exec-high`
Inputs: §1 "Map data", "Site model", "Tower ↔ site" rows; the site model (read only; building extrusions are named with OSM way ids); tokens.
Steps: (1) `tools/fetch_osm.py`: three Overpass queries (`[out:json][timeout:180]`): city bbox (coastline, `waterway=river`, `highway` motorway/trunk/primary/secondary, the City of Chicago boundary relation), corridor bbox (all `highway`, `building`, river, `railway=rail`), and the site ways by id (`way(id:…)`); cache to `_local/osm_*.json`; a re-run skips existing files. (2) Geo-registration: footprint polygon of each `buildings` extrusion (bottom profile) vs the matching OSM way projected to Web Mercator; fit a similarity transform (scale, rotation, translation; Procrustes on vertex sets) over ≥ 20 matched buildings; report RMS residual, scale and rotation. (3) `tools/render_map.py` → `assets/map-city.svg` (lake and river `#F2F1ED` fills, roads hairlines `#B5B5B5` / `#D9D9D9` by class, boundary hairline ink) and `assets/map-corridor.svg` (buildings `#E4E4E2`, streets, river, rail, Randolph St from Michigan Ave to the site-model west edge as the `corridor` group, the site-model extent as the `sitebox` group, everything else in `rest`); `viewBox` in map metres; mono 11 px attribution `Map data © OpenStreetMap contributors`. (4) `data/site.json`: transform, site-model extents and `Site` polygon in map coordinates, Randolph centreline, corridor length in miles, Mercator origin. (5) Captures (both SVGs at 1920×1080); commit `map: OSM city + corridor SVGs, site registration`; log entry with the residual.
Outputs: two SVGs, `data/site.json`, two tools. Acceptance: RMS residual < 1.5 m; scale = 0.3048 × Mercator factor at 41.88° ± 1 %; SVGs < 1.5 MB each, render in headless Edge, groups `rest` / `corridor` / `sitebox` present, token colours only; attribution present.

### S14 · Site GLB · 25 min · `cs-exec-high`
Inputs: the site model (read only), `data/site.json`, tower GLB facts (§1), `Randolph_Master_v1.1.3dm` (read only) for the podium cross-check, Blender 5.2 headless only if decimation is needed.
Steps: (1) `tools/build_site_glb.py` with rhino3dm + numpy: take `buildings` (`Extrusion.GetMesh`), `TERRAIN_MESH`, `Bridges`, `Roads` (render mesh if present), `Site` outline as a 1 ft band; skip `Earth`, `Setup::*`, `TPX_TERRAIN`, `Rail`. (2) Remove the building extrusions whose footprint centroid lies inside the `Site` polygon (the existing on-site structures); list their ids. (3) Write `assets/site.glb` directly (JSON + BIN chunks, POSITION + indices accessors, one primitive per group, one grey material per group from the S5 palette), feet → metres, root node rotation `[-0.7071, 0, 0, 0.7071]`, origin = site-model origin. (4) Tower placement: fit the F_POD footprint (97.84 × 63.40 m) onto the `Site` polycurve's rectangle (GLB x runs N–S); cross-check the result against the podium outline in the master model; write `towerOffset` [x, y, z] m and `towerYawDeg` into `data/site.json` (the site context is moved by the inverse so the tower stays at the scene origin). (5) If the GLB > 12 MB, decimate terrain and bridges with `tools/decimate_blender.py` (`blender -b --python … --`), never the buildings; check-page capture with the vendored GLTFLoader; commit `site: context GLB, tower placement`; log entry with face counts per group.
Outputs: `assets/site.glb`, `tools/build_site_glb.py`, (`tools/decimate_blender.py`), `data/site.json` extended. Acceptance: GLB ≤ 12 MB, loads without errors; extents in metres = model feet × 0.3048 ± 0.1 m; tower footprint inside the `Site` polygon, every edge within 1.0 m of the podium outline; on-site buildings removed (ids listed); excluded layers absent.

### S15 · Intro Sequence · 30 min · `cs-exec-top`
Inputs: both map SVGs, `data/site.json`, `assets/site.glb`, `js/tower.js` (scene, camera, `yawFor`, `show`), deck API, §1 "Intro timing".
Steps: (1) `js/intro.js` + `css/intro.css`: a stage machine on `requestAnimationFrame` with ease-in-out-cubic; the two SVGs stacked full-viewport over the title slide, zoomed by a matrix transform on their root `<g>` (A: whole city SVG → Chicago scale, the city boundary filling the viewport height; hold). (2) B: `#rest` opacity → 0.3; `#corridor` draws in accent (stroke-dashoffset) with `#sitebox` in ink; C: zoom until Randolph from the Loop to the site box fills the width; mono caption `Randolph St · Michigan Ave → 735 W Randolph · <miles> mi` from `site.json`; hold. (3) D: `tower.js` loads `site.glb` into the same scene as a `context` group at the inverse tower offset; the camera starts straight down above the site model at the altitude where the model's extent matches the SVG frame (fov 28), the map fades out as the canvas fades in, then yaw/pitch/distance tween over 3 s to the S5 title camera (yaw 31.95°, pitch −7.74°) with the context visible around the tower; title text fades in. (4) Hooks: plays once on load at `#01`; any key or click skips to the final frame; `I` replays; `prefers-reduced-motion` → final frame; leaving `#01` fades the context out over 900 ms and returning fades it back; below 900 px only stages A–C play in the sticky band. (5) Captures at stages A, B, C, D-end and the title (1920×1080); README paragraph; `CHANGELOG.md`; tag (next free minor); commit `intro: map zoom, corridor, site descent`; log + PROJECT_LOG entries; mirrors.
Outputs: `js/intro.js`, `css/intro.css`, edits to `js/tower.js` and `js/app.js`, captures, tag. Acceptance: durations per §1 (12–14 s total, measured); at the cut frame the SVG `#sitebox` and the 3D site extent overlap within 1 % of the viewport width (overlay capture); final camera = S5 title camera; skip, replay and reduced-motion work; title text visible ≤ 3 s after load even while `site.glb` streams; slide count and counter unchanged (18 at present); attribution visible on A–C; no new hue; no console errors.
Gate: `STOP - report whether the intro reads right on your screen (play it twice, once with I) before I continue.`
Handoff: S16 (which checks its own start time).

### S16 · Site Access Layer · 30 min · `cs-exec-high` · skip if it would start after 21:30
Folds in review notes v1.1 T9 (slide C3). Inputs: `<ROOT>\02_Site\Diagrams\735WRandolph_SiteAccess_Diagram_v1.0.pdf` (Affinity export, vector, 2560 × 1440 pt, north up; mode strokes: green pedestrian, orange car, pink Green/Pink Line, blue Blue Line, cyan bike, purple bus, P parking), `data/site.json` (`Site` polygon in map metres), `assets/map-corridor.svg`, PyMuPDF.
Steps: (1) `tools/extract_access.py`: `page.get_drawings()` → paths grouped by stroke colour (nearest of the seven mode colours, tolerance 0.08 per channel); record the two embedded images' bounds; write raw polylines in PDF points to `_local/access_raw.json`. (2) Georeference with two control points: two footprint corners of the ground-floor plan in the PDF against the same corners of the `Site` polygon in map metres (similarity transform); report the residual on a third corner. (3) `assets/map-access.svg` in map metres (the corridor map's `viewBox` convention): groups `walk`, `car`, `cta-pink`, `cta-blue`, `bike`, `bus`, `parking`, `entrances` (hotel on Halsted with the drop-off, office on Washington: accent, the only accent use), `loading` (Halsted → the private drive south of the historic buildings, Brad 2026-09-25; dashed; `[BRAD TO CONFIRM]`); mono labels Randolph St, Washington Blvd, Halsted St, Kennedy Expy (I-90), north mark; station names and walk times as `[BRACKETS]` until verified (check the CTA map and the 80 m/min rule; list findings for Brad). Mode colours as in the PDF, logged as an exception to the one-hue rule (review notes T9 default); everything else in greys. (4) Slide and decal: add a `kind: 'image'` entry at the head of `story.json` `intro` (before Thesis) with the SVG, label `Site access`, caption `Fig. 0n — Site access, 735 W Randolph`; rasterise the SVG with headless Edge at 4096 px to `assets/access-decal.png` and drape it as an alpha plane at grade in the 3D context group (toggle `accessDecal` in `site.json`) so the routes show during the descent and on the title frame. (5) Captures (slide at 1920×1080 and 390 px; title frame with the decal); commit `access: site-access layer, slide, ground decal`; log entry with the control-point residual and the fact checks; new copy lines into the copy-status table.
Outputs: `tools/extract_access.py`, `assets/map-access.svg`, `assets/access-decal.png`, `story.json` entry, context decal. Acceptance: control-point residual < 2 m; seven mode groups present; accent only on the two entrances; labels as listed; slide renders at both widths; decal edges within 1 m of the site polygon in a top-down capture; no console errors.
Handoff: S10 if the time is ≤ 22:00 and `_local/cf.env` exists; otherwise the project closeout block.

### S10 · Comment API · 15 min · `cs-exec-medium` · conditional
Condition, checked first: S16 done or skipped (log entry) and the time ≤ **22:00**, and `_local/cf.env` present (§7 item 6). If either fails: skip S10–S12, note it in the log, hand off to S8.
Inputs: `_local/cf.env`, Cloudflare API v4, §1 "Comment API" row.
Steps: (1) `worker/comments.js`, ES-module Worker with KV binding `COMMENTS`: `GET /c/<room>` → JSON array; `POST /c/<room>` with `{name, slide, text, strokes}` → appends `{id, t (ISO), name, slide, text, strokes}`, returns it with 201; `OPTIONS` → 204. Validation: room `^[a-z0-9]{6}$`; name 1–40 chars; slide integer 1–40 (the deck's slide count varies); text 0–500 chars; strokes = array of polylines of `[x, y]` integers 0–1000, serialised ≤ 20,000 bytes; text or strokes required; 200 comments per room, then 413. CORS allow-origin only for `https://arch575.bradmachado.com` and `http://localhost:8000`, else 403; other paths 404. Storage: one KV value per room (`room:<room>`), read-modify-write. (2) `tools/cf_deploy.py` (stdlib `urllib`): read `_local/cf.env`; create or reuse KV namespace `arch575_comments` (`GET`/`POST /accounts/{id}/storage/kv/namespaces`); `PUT /accounts/{id}/workers/scripts/arch575-comments` as multipart with part `metadata` = `{"main_module":"comments.js","compatibility_date":"2026-09-01","bindings":[{"type":"kv_namespace","name":"COMMENTS","namespace_id":"<id>"}]}` and part `comments.js` typed `application/javascript+module`; `POST …/scripts/arch575-comments/subdomain {"enabled":true}`; `GET /accounts/{id}/workers/subdomain` (if none, `PUT {"subdomain":"bradmachado"}`; if that fails, ask Brad); print `https://arch575-comments.<subdomain>.workers.dev`. Never print the token. (3) curl round trip from the scratchpad: fresh room `GET` → `[]`; `POST` one comment with a two-point stroke → 201; `GET` → 1 item; `OPTIONS` with `Origin: https://arch575.bradmachado.com` → 204 + allow header; `Origin: https://example.com` → 403; room `ABC` → 400. (4) Room code: 6 chars `[a-z0-9]` from Python `secrets`; write `data/review.json` `{"api": "<url>", "room": "<code>", "pollMs": 10000, "maxName": 40, "maxText": 500}`. (5) Commit `review-api: worker, kv, deploy script`; log entry with URL, room, the six curl results.
Outputs: `worker/comments.js`, `tools/cf_deploy.py`, `data/review.json`. Acceptance: the six curl results; `git grep CF_API_TOKEN` finds only the env reader; `index.html` unchanged.

### S11 · Phone Comments · 20 min · `cs-exec-high` · conditional
Inputs: `data/review.json`, deck API (`js/app.js` header comment), S4 scroll layout, `css/style.css` tokens (`btn`, inputs). The plan `<img>` is letterboxed (`object-fit: contain`): the drawing surface must be sized to the image's content box (from `naturalWidth`/`naturalHeight`), not the element box.
Steps: (1) `js/review.js` + `css/review.css`, loaded by `app.js` after `deck.ready` only when `location.search` has `review=<room>` or `present=<room>`; with neither, no request and no DOM change. Reviewer mode: under every slide's plan (title and site slides: under the text) a `btn` "Comment on <label>"; tap opens a panel: name `<input>` (40 chars, kept in `localStorage`), text `<textarea>` (500), drawing surface `<svg viewBox="0 0 1000 1000">` over the plan content box capturing pointer polylines (2 px accent while drawing; hidden on title and site), Undo / Clear / Send. Send `POST`s to `<api>/c/<room>`; success swaps the panel for "Sent, <name>." and lists the comment under the level; failure shows "Not sent. Retry." and keeps the draft. (2) Reviewer mode also works at desktop widths (panel under the plan column). (3) `tools/make_qr.py` (`pip install segno`) → `assets/qr-review.svg` for `https://arch575.bradmachado.com/?review=<room>`, ink `#171715` on white; `app.js` shows it on the title slide bottom-left (112 px) with the mono URL, in present mode only. (4) Captures: 390×844 level slide with the panel open and one stroke; 1920×1080 title slide in present mode. (5) Commit `review-ui: phone comments, sketch capture, QR`; log entry.
Outputs: `js/review.js`, `css/review.css`, `tools/make_qr.py`, `assets/qr-review.svg`, two small edits in `js/app.js`. Acceptance: no query parameter → no worker request, `document.body.innerHTML` identical to the previous commit, slide count and counter unchanged; a POST from the 390 px layout lands in KV; a stroke along the plan's left edge has x ≈ 0, along the bottom edge y ≈ 1000; name persists; failure state works; accent the only hue; no `[BRACKETS]`; no console errors.

### S12 · Presenter Overlay · 20 min · `cs-exec-top` · conditional
Inputs: S10 API, S11 module, `window.deck` (`count` = `state.slides.length`; add a minimal `deck.append(slide)` that pushes `{index, kind: 'comments', level: null, levelIndex: −1, el}` and refreshes the counter), `window.tower.show(levelIndex, instant)`.
Steps: (1) Present mode (`?present=<room>`, ≥ 900 px): append a final slide `kind: 'comments'` (hash = count + 1); the counter grows by one in present mode only. The slide lists comments in deck order then time: mono `HH:MM`, name, text, a `[sketch]` mark when strokes exist; the tower shows no highlight on this slide. (2) Poll `GET` every `pollMs`; a mono badge beside the counter reads `n comments` (hidden at 0) or `offline`; nothing else changes on error. (3) Click a comment → `deck.go(slide − 1)`; the plan gets an overlay `<svg viewBox="0 0 1000 1000">` aligned to the plan content box: 2 px `#B0431F` polylines, round joins, mono name tag top-left of the plan. Keys: `C` toggles the overlay, `Esc` returns to the comments slide, `[` / `]` previous / next comment. (4) End to end with curl: POST two comments (one with strokes along the left and bottom edges of the L18–32 plan: `[[[0,0],[0,1000]],[[0,1000],[1000,1000]]]`); open `?present=<room>#<count+1>` in headless Edge → both listed within 10 s, badge `2 comments`; click the second → the L18–32 slide with strokes on the plan's left and bottom edges; captures of both. (5) Commit `review-overlay: comments slide, stroke overlay`; tag `v1.1.0` (or `v1.2.0` if S8 already took `v1.1.0`); `CHANGELOG.md`; README "Review mode" paragraph (the two URLs, the keys); log + PROJECT_LOG entries; mirrors.
Outputs: `js/review.js` (extended), `js/app.js` (`deck.append`), README, tag. Acceptance: step 4 passes; `C`, `Esc`, `[`, `]` work; no query parameter → site unchanged (slide count, counter, no worker request); no console errors; comments slide uses only tokens and the accent.
Gate: `STOP - report the result of scanning the QR with your phone and sending one test comment before I continue.`
On the day: if the Worker is down, present from the plain URL; nothing on the slides depends on it.

### S8 · Plans v1.3 Model · 20 min · `cs-exec-high` · after Brad saves `Core_Tower_V14_v1.3.3dm`
Steps: (1) Confirm the file exists and its timestamp. (2) Run `Core_V13_PlanFurnished_v1.3.py` with `--nogen L1,L2` into `PlanFurnished_V14_v1.3b\` (bump the script to v1.4 if a change is needed, e.g. removing the lobby cut from handoff §6 item 3 once the model wall is fixed). (3) Diff legend keys against v1.3; visual check of the two office SVGs for duplicate furniture; check the L34 clubhouse opening and pool deck are present. (4) Copy to `assets/plans/`, commit `plans: from V14 v1.3, generators off`; tag `v1.1.0`; log and PROJECT_LOG entries. (5) Re-measure areas if the model changed plates; any change to §1 numbers is a plan revision (v1.1) and a deck update.
Gate: `STOP - report any plate or core number that changed before I continue.`

### S9 · Main-site Link-in · 15 min · `cs-exec-medium` · post-review, only on Brad's instruction
Per subdomain handoff §6: section `04 / Development`, row `D.01`, in a clone of the main repo; one commit; Brad approves before push. Not scheduled.

## 5. Schedule (Wed 2026-10-08, all tonight)

| Block | Subtasks | Minutes | With 20 % buffer | Cumulative |
|---|---|---|---|---|
| Tonight 1 | S0, S1 (+ Brad: GoDaddy CNAME, 2 min) | 30 | 36 | 0:36 |
| Tonight 2 | S2 ∥ S3 | 25 (parallel) | 30 | 1:06 |
| Tonight 3 | S4, S5 | 60 | 72 | 2:18 |
| Meanwhile | DNS propagation, certificate issue, Brad confirms the copy lines | — | — | — |
| Tonight 4 | S6, S7 | 35 | 42 | 3:00 |
| Tonight 5 | S13, S14, S15 (entry intro; start now, S7 is done except the copy gate) | 80 | 96 | 4:36 |
| Tonight 5b | S16 site-access layer (skipped if it would start after 21:30) | 30 | 36 | 5:12 |
| Tonight 6 (conditional) | S10, S11, S12 (if S16 is done or skipped by 22:00 and the Cloudflare token is in place) | 55 | 66 | 6:18 |
| Target | `v1.0.0` live **tonight by 23:00**; hard limit Thu 07:30; review Fri 09:00 | | | |
| Later | S9 (post-review, on Brad's instruction); S8 done | 15 | | |

Fallback at any point: present from `Tower_LevelDeck_v1.7.pptx`, or from the local folder with `python -m http.server` (works without DNS or HTTPS). Review mode never blocks the review: the plain URL is always the `v1.0.0` build.

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
| Cloudflare account + API token (Workers Scripts Edit, Workers KV Storage Edit), workers.dev subdomain | Brad (§7 item 6); S10–S12 only; free tier |
| `segno` (QR SVG) | absent; `pip install segno` in S11 (pure Python). `tools/cf_deploy.py` uses stdlib `urllib` (`requests` absent) |
| Overpass API (OpenStreetMap) | network, public, no key; results cached in `_local/` |
| rhino3dm 8.35.0 mesh access (`Extrusion.GetMesh`, `BrepFace.GetMesh`), numpy 2.2.6 | present; render meshes verified on all 504 breps of the site model (2026-10-08) |
| Blender 5.2.0 LTS (`C:\Program Files\Blender Foundation\Blender 5.2\blender.exe`) | present; headless `-b` only, optional decimation of `site.glb`; never opened as a GUI |
| PyMuPDF 1.28 (`fitz`, `page.get_drawings()`) | present; S16 vector extraction from the site-access PDF |
| Deprecated | PowerPoint Morph with per-slide GLB swap → replaced by the three.js tween. `KHR_materials_pbrSpecularGlossiness` in the deck's box builder is a deprecated glTF extension; the web box uses a plain `MeshStandardMaterial`. |
| Model tiers | S0 lite · S1 S2 S7 S9 S10 medium · S3 S4 S6 S8 S11 S13 S14 S16 high · S5 S12 S15 top |

## 7. For Brad (open items)

1. Review time: confirmed Fri 2026-10-09 09:00.
2. ~~GoDaddy CNAME `arch575` after S1 reports the custom domain is set (S1 gate).~~ Done 2026-10-08 12:40; HTTPS enforced.
3. Confirm or edit the 13 copy lines S2 lists in the log (title, site, 10 descriptions, "Holodeck").
4. Save `Core_Tower_V14_v1.3.3dm` when today's Rhino work is done (triggers S8).
5. Pink area on Office 2 (service car SV-4 + lobby) drawn as back of house: confirm.
6. For S10–S12 (reviewer comments): Cloudflare Account ID and an API token saved as `C:\Users\User\Projects\arch575\_local\cf.env` (two lines: `CF_ACCOUNT_ID=…`, `CF_API_TOKEN=…`). Walkthrough prompt for the Claude app: `docs/prompts/Brad_Cloudflare_Token.md`. Needed before 22:00 for S10 to run tonight.
7. Reviewer names: free text (default). Say if you want a fixed list instead.
8. After S12: scan the QR with your phone and send one test comment (S12 gate).
9. Entry intro: the default is a monochrome OpenStreetMap line map (matches the deck). If you want photographic imagery for the zoom instead, say so before S13 runs: USGS NAIP (public domain) or Google Earth frames with `Imagery © Google`, about 20 min more.
10. Site model moved: `Downloads\Site (1).3dm` → `02_Site\Arch575_BlenderSite_RhinoModel_v2.0.3dm`. The hidden `Earth` layer (Google 3D Tiles) stays out of the website; say if you disagree.
11. After S15: play the intro twice on your screen (once with `I`) and report (S15 gate).
12. S16 site-access layer: the diagram's mode colours stay on that slide and the ground decal (exception to the one-hue rule, review notes T9 default); say if you want greys + accent instead. Its station names, walk times and the loading route come back to you as `[BRACKETS]` with the agent's checks.
13. The 18-row copy gate (progress log) still blocks `v1.0.0`; reply "all confirmed" or row + wording.
14. Review notes T5 (interior views over Google Earth) are not in this plan; run them in the Rhino MCP conversation.
