# arch575.bradmachado.com — Review Notes v1.0 (for the build agent)

Date: 2026-10-08 17:30 CT. Review: Fri 2026-10-09 09:00.
Author: review conversation (Opus 5.5). Role: review only. The build agent executes everything below; this conversation renders nothing further.
Reviewed: live HEAD `0c3a195`, all 12 slides captured at 1920×1080 (headless Chromium), `data/levels.json`, progress log S0–S8, Brad's stated mid-review priorities.
Mirror: `C:\Users\User\OneDrive - University of Illinois - Urbana\Architecture\2026 Fall - Arch 575\03_Design\05_Presentation\Web\Arch575Site_ReviewNotes_v1.0.md`

## 0. Before you start

1. `git pull` in `C:\Users\User\Projects\arch575`. S8 was run from a cloud clone (commits `f83debe`, `0c3a195`); the local clone is behind.
2. **Rule change (Brad, 2026-10-08):** Claude saves the key Rhino model regularly via Rhino MCP `save_doc`, always as the next minor version, never over an earlier file. The "Never save a .3dm" line in `docs/prompts/S*.md` is void. Project `CLAUDE.md` line 19 is already updated.
3. Key model: `...\03_Design\02_Circulation_Structure\Core_Tower_V14_v1.3.3dm` (33,987 objects). Rhino slot `aardvark` (adopted); the open window may still be titled v1.2, so the next save goes to `Core_Tower_V14_v1.4.3dm`.
4. Python on Brad's machine: `C:\Users\User\AppData\Local\Programs\Python\Python310\python.exe` (has rhino3dm + matplotlib). When you launch it from Rhino's `run_python` via `subprocess`, remove every `PYTHON*` variable from `env` and pass `-I`. Otherwise it picks up Rhino's site-packages and fails with `No module named 'matplotlib'`.

## 1. Done — do not redo

| Item | State |
|---|---|
| S8: plans from V14 v1.3 | Done. `tools/Core_V13_PlanFurnished_v1.4.py --nogen L1,L2,V,W` → `assets/plans/PlanColor_<key>_v1.4.svg` ×10 + `legend_v1.4.json`; `levels.json` and `tools/build_levels.py` point at v1.4. Source folder `...\03_Design\05_Presentation\MidReview\PlanFurnished_V14_v1.4_nogenVW\`. Live and verified. |
| v1.4 script change | Rooms on L1/L2 (office) plans are classed OFFICE. Executive offices named `SUITE` were classed HOTEL, and unmatched names fell to AMENITY. |
| `--nogen V,W` | L17 and L34 now show model furniture only. Generated terrace furniture was overlapping the L17 fit-out and the L34 deck furniture. |

## 2. Tasks, in priority order (09:00 deadline)

### T1 — Copy gate (Brad) · blocks `v1.0.0`
- The 13 lines in the progress-log "Copy status" table are still unconfirmed.
- Row 9 (L33) "Substation, water and cooling towers." and row 6 (L16) "Fan rooms and heat exchangers." contradict Brad's 2026-10-02 decision: main plant in the basement (B1); the O1/O2 mech floors are transfer / booster-pump space plus systems that must be at height. Proposed wording for Brad to confirm or edit:
  - L16: "Transfer and booster pumps."
  - L33: "Transfer and booster pumps; rooftop-bound systems."
- Edit `tools/build_levels.py` source copy, not only `levels.json`, so a rebuild keeps the change.

### T2 — Table values stale · 15 min
- Plate / Core / Efficiency / Area rows in `levels.json` come from `MidReview_LevelDeck_v1.3.py` (V14 v1.2 era). They have not been recomputed from V14 v1.3.
- Recompute from `Core_Tower_V14_v1.3.3dm` (slab boundary and core outline areas per plan key). Report any changed value to Brad before pushing.

### T3 — Projector legibility · 10 min, CSS only (`css/app.css`)
| Selector | Now | Change to |
|---|---|---|
| `.deck-header__count` (l.48) | 11 px | 13 px |
| `.data th` (l.236) | 11 px, `--color-faint` #98978F | 13 px, `--color-muted` #6B6B67 |
| `.key__label` (l.276) | 10 px | 13 px |
| `.plan__scale text` (l.322) | 10 px, faint | 13 px, muted |
| `.slide figcaption` | 10 px, faint | 13 px, muted |
- Do not edit the vendored `css/style.css`; override in `app.css`.
- Check the 390 px phone layout after the change (no horizontal scroll).

### T4 — Missing story slides · largest gap
Brad's stated mid-review priorities: jump into the thesis, diagrams, strategy; walk the office lobby and the hotel lobby (what guests see); show the holodeck. Facade appears only as a few renders. Current deck: title, site, 10 levels. Missing:
1. Thesis / strategy slide (text cols 1–6, one diagram).
2. Stacking diagram + totals: office plate sf vs 812,500 target (10 × 39,930 + 15 × 28,578 = 827,970 at current table values; update after T2); keys 7 × 23 + 6 × 24 = 305 vs 300.
3. Ground floor (office lobby + hotel lobby). Check first whether an L01 plan exists in V14 v1.3. As of 2026-09-25 L0 was not drawn. If it is absent, report to Brad; do not invent a plan.
4. Podium L01–L04 (parking): the deck jumps B1 → L05.
5. Facade renders (2–3): pull from existing renders. Do not generate new ones.
6. Closing / questions slide.
- Implementation: `js/app.js` only knows the slide kinds `title | site | level` (l.257–269). Add a generic `image` / `text` kind driven by a new `levels.json` array. The tower highlight should hide on these slides (as on title/site).
- Any copy written for these slides goes to Brad for confirmation (same gate as T1).

### T5 — Interior views over Google Earth · coordinate with the Google Earth conversation
Brad wants interior 3D views from inside the building, with the Google Earth view behind the glazing, so reviewers see the view from each floor.
- **Camera convention (already set, `PROJECT_LOG.md` 2026-10-07):** Earth Web URL `@<lat>,<lon>,<alt>a,1d,<fov>y,<heading>h,90t,0r`.
  - Site centroid ≈ 41.8837, −87.6460.
  - Grade ≈ 181 m ASL.
  - alt = grade + floor z + 5 ft eye.
  - Hotel L35 at 539 ft, 11.5 ft floor-to-floor (L45 floor z = 654 ft).
  - Existing frames: `02_Site\Photos_Survey\735WRandolph_L45-SSW_GoogleEarth_v1.0.jpg` (heading 202.5), `..._L45-W_GoogleEarth_v1.0.jpg` (heading 270).
- **Rhino side:**
  - Perspective camera inside the room at floor z + 5 ft.
  - Model axes: X east, Y north, feet, footprint corner at origin.
  - Same heading and FOV as the Earth frame.
  - Capture with `_-ViewCaptureToFile` with a transparent background so the glazing reads as alpha.
  - Composite the Earth frame behind it (PIL).
  - Restore Brad's viewport camera afterwards; use the MCP only, no computer use while he is at the machine.
- **Camera match must be verified:**
  - Earth Web's `y` value may be vertical, not horizontal, FOV. Confirm by aligning one landmark (e.g. Willis Tower) in a test pair before batching.
  - The camera x,y must be the same point in both: convert the Rhino eye point to lat/lon. Do not reuse the site centroid for every room.
- **Image quality:** current Earth frames are browser screenshots, 1568 × 778, with UI chrome. Prefer Google Earth Pro "Save Image" (no chrome, higher resolution) or Photorealistic 3D Tiles in Blender, which the other conversation listed as its next step; Tiles gives one camera, no compositing.
- **Attribution:** keep Google attribution visible on every composite (caption: "Imagery © Google").
- **Views, in order:**
  1. L45 suite SSW + W (Earth frames exist; pilot).
  2. L34 window bar facing downtown (E).
  3. L17 coworking.
  4. L18–32 corner executive office.
  5. L05 ballroom wing (W).
- **Site integration:** per-level "View" image toggled with the plan (or a before/after slider between model-only and composite); file names `View_<key>_<heading>_v1.0.jpg` in `assets/views/`.

### T6 — Plan graphics (design call — ask Brad, default: no change tonight)
- The level's own program is filled in full-strength accent, so the plans read as solid oxide slabs and the furniture as specks.
- On L16 / L33 the whole mech floor is accent, so it reads as a hero floor.
- Option: hero program at a 40–60 % tint of #B0431F, full accent for one move per slide, MEP floors in greys.

### T7 — Backup deck stale
`...\03_Design\05_Presentation\Tower_LevelDeck_v1.7.pptx` still carries the V14 v1.2 plans. Re-run `05_Analysis_Tools\MidReview_LevelDeck_v1.3.py` against the v1.4 plans (PNG: `Core_V13_PlanFurnished_v1.4.py ... --fmt png --nogen L1,L2,V,W`) → `Tower_LevelDeck_v1.8.pptx`.

### T8 — Model gaps (report to Brad, do not draw)
- L34: the west and perimeter deck has no model furniture. With generators off, it renders empty.
- 3D tower = `TowerModel_GLB_v1.0` (template export), not a V14 export. Verify the massing against V14 (Office 2 south trim, stack heights) before the review, or note it as schematic.

## 3. Verified OK (no action)
- HTTPS, 404, CNAME, main-site links (S6).
- Normal keyboard navigation is clean. A faded site image behind B1 appeared only when jumping by URL hash in headless capture; not a site defect.
- Legend keys per level unchanged after S8.
- Tower turns 36° per level; highlight boxes match the level ranges.

## 4. Reporting
- On completion of each task, append a progress-log entry (template at the top of the log) and one `PROJECT_LOG.md` entry per session.
- Any copy, number change or design call goes to Brad as a single STOP question.
