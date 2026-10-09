# arch575.bradmachado.com

ARCH 575 mid-review presentation (Fall 2026): West Loop Gateway, a mixed-use office + hotel tower at 725 W. Randolph St., Chicago. Brad Machado, M.Arch, Illinois School of Architecture.

Static site: title, site, and ten levels. Each level shows a rotating three.js tower with that level highlighted, a furnished floor plan, and a short data table.

Entry intro (slide 01, `js/intro.js` + `css/intro.css`): a 12.8 s sequence plays once on load. A monochrome OpenStreetMap city sheet (`assets/map-city.svg`) zooms to Chicago scale, the map greys out while Randolph St draws in the accent from Michigan Ave to the site model, the view zooms to the corridor (`assets/map-corridor.svg`) with a mono caption, then the map cross-fades to a top-down three.js view of the site context (`assets/site.glb`, placed by `data/site.json`) at the same framing and the camera descends to the title view with the tower standing on the site. Any key or click skips to the final frame, `I` replays it, `prefers-reduced-motion` shows the final frame only, and below 900 px only the map stages play in a 40vh band. The site context stays around the tower on slide 01 and fades out over 900 ms on leaving it. Map data © OpenStreetMap contributors.

Site loop (slide 02, `js/siteloop.js` + `css/siteloop.css`): at ≥ 900 px the site photo gives way to the same three.js context, greyed out (every context colour lerped 60 % toward the page background) under one fixed oblique camera from the south-south-east (site centred, Halsted St at the left third, the Kennedy Expressway at the right edge). The named feature nodes of `assets/site.glb` (rebuilt by `tools/build_site_glb.py` v1.1: `r_randolph`, `b_restaurantrow`, `r_halsted`, `r_washington`, `b_skybridge`, `Site`; the streets are ribbon meshes from the OpenStreetMap centrelines) cross-fade to the accent one at a time, 2.4 s per step, then the site plate turns accent and the tower fades in as a ghost (translucent fill, ink edges), holds 8 s, and the cycle restarts (23.8 s; `LOOP = false` holds on the site). Slides 01 and 02 are one continuous shot: the camera tweens between the title view and the site view over 1.5 s while the solid tower dissolves or returns. A mono caption names the active feature; `I` on slide 02 restarts the loop; `prefers-reduced-motion` shows the final frame; below 900 px, without WebGL, or if the context fails the photo slide stays. `?loopat=1..6|ghost` freezes a step for captures.

## Run locally (also the offline mode for the review)

```
cd C:\Users\User\Projects\arch575
python -m http.server 8000
```

Open `http://localhost:8000`. Arrow keys move between slides; `F` toggles fullscreen. Module scripts and the GLB do not load from `file://`.

## Layout

| Path | Contents |
|---|---|
| `index.html`, `css/`, `js/`, `data/`, `assets/` | the site (GitHub Pages, branch `main`, root) |
| `js/vendor/` | three.js, pinned version in `CHANGELOG.md` |
| `tools/` | Python build scripts (levels.json, vendoring, plan render mirrors) |
| `docs/` | build plan, progress log, agent prompts, reference handoffs |

## Versioning

Git tags mark releases (`v0.1.0` placeholder → `v1.0.0` review build → `v1.1.0` plans from the saved V14 v1.3 model). See `CHANGELOG.md`. Plan and log documents carry their own `v<Major>.<Minor>` in the filename; superseded copies go to `docs/_superseded/`, nothing is deleted.

Backup for the review: `Tower_LevelDeck_v1.7.pptx` in the ARCH 575 project folder (not in this repo).
