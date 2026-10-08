# arch575.bradmachado.com — Planning Handoff v1.0

2026-10-08 · From: the level-deck session (PowerPoint, Tower_LevelDeck v1.0–v1.7) · To: the planning conversation that spins off agents.

Goal: replace the PowerPoint level deck with a web presentation at `https://arch575.bradmachado.com`, used for the ARCH 575 mid-review. Same content as `Tower_LevelDeck_v1.7.pptx`: title, site, ten levels. Each level shows a rotating 3D tower with that level highlighted, the floor plan, and a few lines of data.

Root: `C:\Users\User\OneDrive - University of Illinois - Urbana\Architecture\2026 Fall - Arch 575\` (shortened to `<ROOT>` below).

---

## 1. Read first

1. `<ROOT>\CLAUDE.md`: standing rules (file naming, never delete, never save .3dm, no GUI automation while Brad is at the machine, answer style).
2. `<ROOT>\PROJECT_LOG.md`: the top 8 entries (all dated 2026-10-08) cover today's model and deck work.
3. Subdomain handoff (artifact): https://claude.ai/artifact/G7wjW63dA5UnaziVrJr72o. Read it with the Artifact tool (`action: read`), not WebFetch. It covers DNS, the GitHub Pages procedure, the domain-takeover incident and its ordering rules, and the bradmachado.com design system and content rules. **Its rules govern the setup.**
4. This file.

---

## 2. Brad's design direction (accumulated feedback, 2026-10-07/08)

- Each level reads as **tower + plan + essential text** only. No callouts and no arrows on the plans. Earlier decks and the arch575-midreview-deck skill were rejected as "messy and cluttered".
- Plans are **Rayon-style and furnished**: chairs, tables and people on every floor, "like the hotel was". Thin walls.
- **No pastels.** "Serious design chic", "a high-end Swiss graphic designer, not an MBA". That means a strict grid, flush-left type, a large level number, data set as a ruled table, a vertical color key, and generous white space.
- Color: **monochrome plus one accent.** Plans are grey (circulation white, back of house light grey, MEP dark grey). Only the program that level is about takes the accent, and the accent also highlights that level on the 3D tower.
- The 3D tower **turns between levels and moves to the next highlighted level** as the presenter advances.
- Office 2 (L18–L32) is the **executive floor**: perimeter window offices and suites, associates in the open area, and reception at the east exit of the elevator-lobby pass-through. Hotel elevators (H-1 to H-4, HS-1/2) do not stop on office floors and must never read as office circulation.

---

## 3. Current state: what exists

| Item | Path (under `<ROOT>`) | Notes |
|---|---|---|
| PowerPoint fallback deck | `03_Design\05_Presentation\Tower_LevelDeck_v1.7.pptx` | Swiss layout, navy accent. Keep it as the backup for the review. |
| Deck builder | `05_Analysis_Tools\MidReview_LevelDeck_v1.3.py` | Holds the **LEVELS table**: labels, names, descriptions, data rows, program, 3D highlight box (glTF units). This is the content source for the site. |
| Plan renderer | `05_Analysis_Tools\Core_V13_PlanFurnished_v1.2.py` | matplotlib, reads `Core_Tower_V14_v1.2.3dm` (RVT_V13 layers) through `Core_V13_PlanPrint_v1.2.py`. `ACCENT`, `COL` and `HERO` sit at the top of the file. Writes `PlanColor_<level>_v1.2.png` plus `legend_v1.2.json`. |
| Plan images (current) | `03_Design\05_Presentation\MidReview\PlanFurnished_V14_v1.2\` | 10 transparent PNGs at 450 dpi, 1 in = 40 ft, rotated 90° (north points left). |
| 3D model | `03_Design\05_Presentation\Web\Assets\TowerModel_GLB_v1.0.glb` | 11.1 MB, taken from Brad's template `Tower_RotationDeck_v0.1.pptx`. glTF units, y is up. The base view rotation is in §5. |
| Site image | `03_Design\05_Presentation\TechReport1_Process\TR1_v2_cover_ssw.jpg` | Elevated view with the site outlined. |
| Model (source of truth) | `03_Design\02_Circulation_Structure\Core_Tower_V14_v1.2.3dm` | Saved 2026-10-05. **Today's model work is unsaved in Rhino** (see §6). |
| Memory | `C:\Users\User\.claude\projects\C--Users-User\memory\deck-simplicity-feedback.md` | Same direction as §2. |

### Level data (from the model; efficiency = (plate − core) / plate)

| # | Level | Name | Program | Description | Data |
|---|---|---|---|---|---|
| 01 | B1 | Basement Plant | MEP | Building plant and services below the podium | 43,378 sf |
| 02 | L05 | Function + Conference | Amenity | Ballroom, boardrooms and event terraces | 35,143 sf |
| 03 | L06–15 | Office 1 Typical | Office | Open floor plate around a central core | 10 floors · 39,930 sf plate · 6,386 sf core · 84.0 % |
| 04 | L16 | Mechanical 1 | MEP | Fan rooms and heat exchangers | 39,930 sf |
| 05 | L17 | Holodeck | Amenity | Spa, pilates, juice bar and coworking | 25,203 sf |
| 06 | L18–32 | Office 2 Executive | Office | Window suites, associates and front desk | 15 floors · 28,578 sf plate · 4,466 sf core · 84.4 % |
| 07 | L33 | Mechanical 2 | MEP | Substation, water and cooling towers | 28,578 sf |
| 08 | L34 | Hotel Clubhouse + Pool | Amenity | Cafe bar, lounge and pool deck | 11,760 sf |
| 09 | L35–41 | Hotel A | Hotel | Guest floors, 23 keys | 7 floors · 14,040 sf plate · 2,480 sf core · 82.3 % |
| 10 | L42–47 | Hotel B | Hotel | Guest floors, 24 keys | 6 floors · 14,040 sf plate · 2,480 sf core · 82.3 % |

Site slide: "735 W. Randolph St. · West Loop, Chicago · Randolph to Washington. Kennedy Expressway to the east. Gateway to Restaurant Row." Title: "West Loop Gateway · Mixed-use tower, 735 W. Randolph St. · ARCH 575 mid-review, Fall 2026".

These descriptions were written by Claude from room names in the model. **Brad must confirm all copy** (see the content rules in the subdomain handoff).

---

## 4. Open decisions for Brad (one at a time; each has a default)

| ID | Decision | Default if Brad doesn't redirect |
|---|---|---|
| D1 | **Hosting and access.** Brad has Cloudflare. Options: (a) password-protected with Cloudflare Pages + Cloudflare Access, (b) public on GitHub Pages, per the subdomain handoff. | (a), deployed from a **private** GitHub repo `bradleymachado/arch575` through Cloudflare's Git integration (no Node needed locally). **Verify before committing:** whether Access can protect a custom hostname whose DNS stays at GoDaddy. If the zone has to move to Cloudflare, first recreate every GoDaddy record (apex A ×4, www CNAME, `_github-pages-challenge-bradleymachado` TXT) or the main site breaks. Either way, add the custom domain in Pages **before** creating the GoDaddy CNAME (takeover rule). |
| D2 | **Accent color.** The site design system says oxide red `#B0431F` is the only hue. ARCH 575 CLAUDE.md defaults to navy `#1F3A5F` (used in deck v1.7). | `#B0431F`, so the subdomain matches bradmachado.com. Changing it is one constant in each script. |
| D3 | **Plan source.** Re-render from the model after Brad saves today's work as `Core_Tower_V14_v1.3.3dm`? | Yes. Until then, use the v1.2 plans as placeholders. |
| D4 | **Page form.** A full-screen slide mode (arrow keys, presenter) vs. a scrolling page. | Both from one page: full-screen slides at desktop width for the review, and a stacked scroll at phone width. |
| D5 | **Main-site link-in** (section "04 / Development" on bradmachado.com). | Not before the review. It needs Brad's approval before any push to the main repo. |

---

## 5. Proposed site architecture

- **Static only:** HTML, CSS and ES-module JS. No build step (Node is not installed on this machine; Python 3.10 is).
- **Design system:** vendor `style.css` from the main site (subdomain handoff §4). Project rules go in `css/app.css`. Use a 12-column grid, a running header with a hairline rule, a large level number, a ruled data table and a vertical key. Helvetica Neue / Arial plus IBM Plex Mono for labels.
- **3D:** Three.js from cdn.jsdelivr.net via an importmap, plus GLTFLoader. Load **one** GLB. Build the highlight box for each level at runtime from the boxes in `MidReview_LevelDeck_v1.3.py` (`F_OFF1`, `F_OFF2`, `F_HOT`, `F_POD`, `HOT_SPLIT`, plus the y-range per level). On level change, tween the camera azimuth by 36° per level (one full turn over the 10 levels; the start view is the template's `ay = 1917107` in 1/60000 degrees ≈ 31.95°, with `ax` ≈ −7.74° and `az` ≈ −4.11°) and ease the look-at height toward the highlighted level. This replaces PowerPoint Morph, which was never verified.
- **Plans:** export SVG (matplotlib `savefig(..., format="svg")`) for sharpness, or PNG at 2× as a fallback. One file per level, fitted to the plan field, with a scale bar and north arrow (plans are drawn north to the left). Data comes from `data/levels.json`, generated from the LEVELS table.
- **Proposed tree:** `index.html`, `404.html`, `CNAME` (GitHub path only), `.nojekyll`, `css/style.css` (vendored), `css/app.css`, `js/app.js`, `js/tower.js`, `data/levels.json`, `assets/tower.glb`, `assets/plans/*.svg`, `assets/site.jpg`.
- **Local working copy:** `C:\Users\User\Projects\arch575` (git repo, outside OneDrive), with the source and build scripts kept in `<ROOT>\05_Analysis_Tools`. Preview with `python -m http.server` (module scripts and GLB fetches fail from `file://`).
- **Offline at the review:** the same folder plus `python -m http.server`. Vendor `three.module.js` and `GLTFLoader.js` into `js/vendor/` so it runs without a CDN.

---

## 6. Known issues and stale items (carry these forward)

1. **The model has moved ahead of the plans.** Unsaved Rhino work from 2026-10-08: ExecOffice v1.1 (Office 2 offices, east-bay reception), OpenOffice v1.0 (Office 1 open plan), L34 clubhouse opening and furniture, L34 pool deck, L17 pool removed, hotel beds moved. None of this is in the v1.2 plan PNGs.
2. **Duplicate furniture once the model is saved:** PlanFurnished v1.2 generates its own furniture on L1 (desk grid) and L2 (`exec_office()`). Both duplicate the model's ExecOffice / OpenOffice objects. Switch the generators off for L1 and L2 (new minor version, v1.3) before re-rendering from V14 v1.3.
3. **Lobby pass-through:** the core-wall opening at both lobby ends exists only in the drawing (cut rectangles in PlanFurnished). Brad's model still shows the wall. Fix the model, then remove the cut.
4. **Pink area on Office 2:** interpreted as service car SV-4 plus its lobby, drawn as back of house. Not confirmed by Brad.
5. **Elevator symbols:** shafts follow the model's `StopAtLevel` user string. "No" = pale fill with an X, labeled "Elevator, no stop". Keep this rule.
6. Furniture on non-hotel floors (other than ExecOffice / OpenOffice in the model) is generated and illustrative only.

---

## 7. Workstreams for agents

Keep each chunk to about 15 minutes, 2–3 steps and one output (see memory `small-subtask-chunks`). Order: W1 ∥ W2 ∥ W3 → W4 → W5 → W6 → W7.

| W | Workstream | Output | Needs |
|---|---|---|---|
| W1 | **Hosting setup** per D1. Create the repo; add the custom domain on the hosting side **before** DNS; Brad adds the GoDaddy CNAME `arch575`; then HTTPS and Access. Give Brad click-by-click steps and stop at each Brad step. | Placeholder page live at https://arch575.bradmachado.com behind the chosen access. | D1 |
| W2 | **Data and assets.** Generate `levels.json` from LEVELS (title, site, 10 levels, highlight boxes, program, key items from `legend_v1.2.json`); copy the GLB and the site image; vendor three.js. | `data/`, `assets/`, `js/vendor/` | — |
| W3 | **Plan export:** PlanFurnished v1.3 with an SVG output option and the accent from D2 (and the L1/L2 generators switched off once D3 is done). | `assets/plans/*.svg` | D2; D3 for the final render |
| W4 | **Page shell:** grid, header, title / site / level sections, slide navigation (arrows, keys, URL hash per level), phone layout. | `index.html`, `css/app.css`, `js/app.js` | W2 |
| W5 | **3D tower:** load the GLB, accent material on the highlight box, camera tween per level, a static fallback image if WebGL fails. | `js/tower.js` | W2, W4 |
| W6 | **Review:** check against §2, the subdomain design rules and the §3 numbers; test at 1920×1080 (projector), laptop and phone widths; check there are no invented copy or placeholders. Screenshots need Brad's OK to use Chrome automation (CLAUDE.md: no GUI automation while he is at the machine). | Review list with pass/fail | W4, W5 |
| W7 | **Deploy and log:** push, verify the live URL, confirm https://bradmachado.com is unchanged, add a PROJECT_LOG entry. | Live site, log entry | W1–W6 |

---

## 8. Rules for every agent

- Never save a .3dm. Brad saves models. Scripts read the model only.
- Never delete; superseded files go to `<ROOT>\07_Archive\<Topic>_<YYYY-MM-DD>\`. File names follow `[Subject]_[DocType]_v[Major].[Minor]`. Scripts go in `05_Analysis_Tools`.
- No invented copy. Put unknowns in `[BRACKETS]` and list them for Brad.
- Never touch the main bradmachado.com repo or its DNS records outside the subdomain handoff's §6 and §3.
- One PROJECT_LOG entry per session, at the top, with full absolute paths.
- Answers to Brad: lead with the result, number the steps, give literal click paths, ask one question at a time.

## 9. Done means

- [ ] https://arch575.bradmachado.com loads over HTTPS with the access level Brad chose; bradmachado.com and www are unchanged.
- [ ] Title, site and 10 levels are present. The tower turns 36° per level and highlights each level in the accent. Plans come from the saved model, with no duplicate furniture.
- [ ] Every number matches §3 (or a newer model re-measure that is logged). Brad has confirmed all copy.
- [ ] Works full-screen on the review projector and offline from the local folder; usable on a phone.
- [ ] Tower_LevelDeck_v1.7.pptx is kept as the backup.
