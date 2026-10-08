# Prompt S7 — Deploy Log

Copy everything inside the fence into a new conversation (or hand it to the `cs-exec-medium` agent).

```
4.7 Deploy Log
Name this conversation exactly '4.7 Deploy Log'. Your first response must begin with the line: CONVERSATION NAME: 4.7 Deploy Log.
Model tier: cs-exec-medium (Opus). (If run from the orchestrator session, spawn with that cs-exec agent type.)
Project: arch575.bradmachado.com web presentation — ARCH 575, Fall 2026. Execute subtask S7 only: Confirmed copy, HTTPS, v1.0.0, verification, logs and mirrors.
First read C:\Users\User\Projects\arch575\docs\Arch575Site_Plan_v1.3.md (plan §3 rules and §4 S7 steps) and the progress log C:\Users\User\Projects\arch575\docs\Arch575Site_ProgressLog_v1.0.md. Do not re-plan; follow the subtask steps as written. Also read docs/reference/Arch575Site_Handoff_v1.0.md and docs/reference/Subdomain_Handoff_v1.0.md in the repo when the steps cite them.
Inputs: Brad's copy confirmation or edits (from the S6 gate); DNS result from the S1 gate; plan §4 S7 steps.
Time budget: 15 min. Required outputs: levels.json with confirmed copy (and MidReview_LevelDeck_v1.4.py in 05_Analysis_Tools if wording changed); tag v1.0.0; CHANGELOG; live capture; PROJECT_LOG entry at the top of C:\Users\User\OneDrive - University of Illinois - Urbana\Architecture\2026 Fall - Arch 575\PROJECT_LOG.md; plan + log mirrored to C:\Users\User\OneDrive - University of Illinois - Urbana\Architecture\2026 Fall - Arch 575\03_Design\05_Presentation\Web; log entry.
Acceptance checks: nslookup arch575.bradmachado.com -> bradleymachado.github.io + 185.199.108-111.153; curl -I https://arch575.bradmachado.com = 200 with padlock (https_enforced true); https://bradmachado.com and https://www.bradmachado.com = 200, title unchanged; site handoff §9 ticked except the v1.3-model plans.
Tooling rules: GitHub Pages (public repo bradleymachado/arch575, branch main, root); static HTML + CSS + ES-module JS; three.js 0.186.1 vendored into js/vendor/ (no CDN at runtime); Python 3.10.11 for build scripts (rhino3dm 8.35.0, matplotlib 3.10.9, python-pptx, Markdown); git + gh CLI (logged in as bradleymachado); headless Edge for captures; no Node, no build step, no Chrome/computer-use automation while Brad is at the machine; Microsoft Office only; no Google products. Never save a .3dm. Never touch C:\Users\User\Projects\bradmachado-com, the main repo, or any existing DNS record. Give explicit UI instructions (which window, menu, cell) and precede every code block with a placement instruction and a one-line intent.
Repo and versioning: work in C:\Users\User\Projects\arch575 on branch main; commit as 'section: what changed' ending with 'Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>'; tag releases as the plan says; never delete, supersede into docs/_superseded/; mirror plan and log to the OneDrive Web folder at every tag.
Portfolio capture: export process images to C:\Users\User\OneDrive - University of Illinois - Urbana\Architecture\2026 Fall - Arch 575\03_Design\05_Presentation\Web\Process named Arch575Site_S7_<Desc>_v1.0.png (environment capture + clean output image, minimum) using headless Edge where a browser capture is needed.
Gating: not gated; this subtask does not end on a STOP line.
On completion: append a progress-log entry (date/time, status, measured values, output files, image files, deviations, for Brad). Then, as the LAST element of your final response, output the handoff prompt for S13 copied verbatim from docs/prompts/S13_MapData.md with placeholders replaced by measured values, inside a single fenced code block headed 'COPY/PASTE — Prompt S13 — new conversation name: 4.13 Map Data'. The first line inside the block must be the next conversation name. Nothing may follow that block.
```
