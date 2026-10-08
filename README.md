# arch575.bradmachado.com

ARCH 575 mid-review presentation (Fall 2026): West Loop Gateway, a mixed-use office + hotel tower at 735 W. Randolph St., Chicago. Brad Machado, M.Arch, Illinois School of Architecture.

Static site: title, site, and ten levels. Each level shows a rotating three.js tower with that level highlighted, a furnished floor plan, and a short data table.

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
