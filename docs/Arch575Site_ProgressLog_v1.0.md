# arch575.bradmachado.com — Progress Log v1.0

Newest entry at the top. One entry per subtask run. Shared state between conversations lives here, not in chat memory.

## Entry template

```
## YYYY-MM-DD HH:MM · S<N> <Short title> · <model tier> · STATUS: done | partial | blocked
Measured: <values the plan's acceptance checks asked for>
Outputs: <full absolute paths, repo-relative paths, commit hash, tag>
Images: <Process capture filenames>
Deviations: <anything not as planned, or "none">
For Brad: <open items, or "none">
```

## For Brad (running list)

1. Review time Fri 2026-10-09 `[BRAD TO CONFIRM]`.
2. GoDaddy CNAME `arch575` → `bradleymachado.github.io` after the S1 gate.
3. Confirm or edit the 13 copy lines (S2 lists them here).
4. Save `Core_Tower_V14_v1.3.3dm` (triggers S8).
5. Pink area on Office 2 = SV-4 + lobby as back of house: confirm.

## Copy status (S2 fills, S6 checks)

| # | Line | Status |
|---|---|---|
| 1 | Title: West Loop Gateway · Mixed-use tower, 735 W. Randolph St. · ARCH 575 mid-review, Fall 2026 | unconfirmed |
| 2 | Site: 735 W. Randolph St. · West Loop, Chicago · Randolph to Washington. Kennedy Expressway to the east. Gateway to Restaurant Row. | unconfirmed |
| 3–12 | Ten level descriptions (handoff §3) | unconfirmed |
| 13 | Level name "Holodeck" (L17) | unconfirmed |

---

## 2026-10-08 12:04 · S0 Env Check · cs-exec-lite · STATUS: done
Measured: Python 3.10.11 · imports rhino3dm 8.35.0, matplotlib 3.10.9, markdown 3.10.3, python-pptx 1.0.2 → `ok` · git 2.55.0.windows.5 · `gh auth status` logged in as `bradleymachado` (keyring; scopes gist, read:org, repo, workflow) · `gh repo view bradleymachado/arch575` PUBLIC, default branch `main` · `nslookup arch575.bradmachado.com` → Non-existent domain (expected). GLB `TowerModel_GLB_v1.0.glb` 11,108,308 bytes, glTF 2.0, Microsoft GLTF Exporter 2.8.3.97: nodes 26, meshes 12, primitives 12, materials 5, accessors 43, vertices 1,878; root node rotation `[-0.7071, 0, 0, 0.7071]` (z-up source → y-up scene); world-space POSITION extents x 0.000–97.841, y 0.000–219.456, z 0.000–63.398 (consistent with §1: x 0–98, y ≈ 220, z 0–63; y up). Raw accessor values are mesh-local and scaled; only the world-space figures compare to §1. Headless Edge: `https://bradmachado.com` → 1920×1080 PNG, 677,680 bytes.
Outputs: scratchpad `bradmachado_1920x1080.png`, `glb_inspect.py`, `glb_world.py` (temporary); this log entry; commit (see git log, `docs: S0 env check log entry`). No tag (S0 has none).
Images: `<ROOT>\03_Design\05_Presentation\Web\Process\Arch575Site_S0_EnvCheck_v1.0.png` (environment capture), `...\Process\Arch575Site_S0_EdgeHeadless_v1.0.png` (clean output, bradmachado.com at 1920×1080).
Deviations: executed by Fable in a direct conversation rather than a Sonnet cs-exec-lite spawn. Note for S5: the GLB declares `extensionsUsed: KHR_materials_pbrSpecularGlossiness` for all 5 materials; three.js GLTFLoader dropped support for that extension in r152, so at 0.186.1 the loader falls back to a default `MeshStandardMaterial` per primitive (expect a console warning, not an error). S5 "keep the model's materials" should be read as: accept the fallback or assign a neutral grey material; no re-export is needed for the environment check.
For Brad: none.

## 2026-10-08 17:30 · Planning · Fable (strategy conversation) · STATUS: done
Measured: toolchain answer = GitHub Pages, public repo, static HTML/CSS/JS, three.js 0.186.1 vendored, Python 3.10.11 scripts, no Node. Cloudflare Access rejected (needs the hostname in a Cloudflare zone). Defaults taken: D2 `#B0431F`, D3 v1.2 plans now then v1.3 model later, D4 slides + phone scroll, D5 after the review. Environment verified: rhino3dm 8.35.0, matplotlib 3.10.9, Markdown 3.10.3, gh logged in as bradleymachado, Edge headless available; `bradleymachado/arch575` did not exist before this session.
Outputs: `C:\Users\User\Projects\arch575\docs\Arch575Site_Plan_v1.0.md`, `...\docs\Arch575Site_ProgressLog_v1.0.md`, `...\docs\prompts\S0_EnvCheck.md` … `S9_LinkIn.md`, `...\docs\reference\Arch575Site_Handoff_v1.0.md`, `...\docs\reference\Subdomain_Handoff_v1.0.md`, `README.md`, `CHANGELOG.md`, `.gitignore`; repo `https://github.com/bradleymachado/arch575` (public), tag `plan-v1.0`. Mirrors: `<ROOT>\03_Design\05_Presentation\Web\Arch575Site_Plan_v1.0.md` + `.pdf`, `Arch575Site_ProgressLog_v1.0.md`.
Images: none (planning).
Deviations: the strategy-plan skill's generic folder set (`01_Assignments` …) was not created; the ARCH 575 folder rules in CLAUDE.md apply instead. The plan PDF twin is produced by headless Edge from Markdown.
For Brad: see the running list above.
