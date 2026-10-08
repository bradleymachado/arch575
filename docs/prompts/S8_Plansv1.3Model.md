# Prompt S8 — Plans v1.3 Model

Copy everything inside the fence into a new conversation (or hand it to the `cs-exec-high` agent).

```
4.8 Plans v1.3 Model
Name this conversation exactly '4.8 Plans v1.3 Model'. Your first response must begin with the line: CONVERSATION NAME: 4.8 Plans v1.3 Model.
Model tier: cs-exec-high (Opus). (If run from the orchestrator session, spawn with that cs-exec agent type.)
Project: arch575.bradmachado.com web presentation — ARCH 575, Fall 2026. Execute subtask S8 only: Re-render plans from Core_Tower_V14_v1.3.3dm with L1/L2 generators off.
First read C:\Users\User\Projects\arch575\docs\Arch575Site_Plan_v1.2.md (plan §3 rules and §4 S8 steps) and the progress log C:\Users\User\Projects\arch575\docs\Arch575Site_ProgressLog_v1.0.md. Do not re-plan; follow the subtask steps as written. Also read docs/reference/Arch575Site_Handoff_v1.0.md and docs/reference/Subdomain_Handoff_v1.0.md in the repo when the steps cite them.
Inputs: Runs only after Brad confirms C:\Users\User\OneDrive - University of Illinois - Urbana\Architecture\2026 Fall - Arch 575\03_Design\02_Circulation_Structure\Core_Tower_V14_v1.3.3dm is saved. Script Core_V13_PlanFurnished_v1.3.py with --nogen L1,L2; plan §4 S8 steps; site handoff §6 known issues.
Time budget: 20 min. Required outputs: PlanFurnished_V14_v1.3b output folder (or v1.4 script if changed); assets/plans/ updated; commit 'plans: from V14 v1.3, generators off'; tag v1.1.0; log + PROJECT_LOG entries.
Acceptance checks: Legend keys per level unchanged vs v1.3; no duplicate furniture on L06-L15 and L18-L32 (visual check of the two SVGs); L34 clubhouse opening and pool deck present; any plate/core number change reported.
Tooling rules: GitHub Pages (public repo bradleymachado/arch575, branch main, root); static HTML + CSS + ES-module JS; three.js 0.186.1 vendored into js/vendor/ (no CDN at runtime); Python 3.10.11 for build scripts (rhino3dm 8.35.0, matplotlib 3.10.9, python-pptx, Markdown); git + gh CLI (logged in as bradleymachado); headless Edge for captures; no Node, no build step, no Chrome/computer-use automation while Brad is at the machine; Microsoft Office only; no Google products. Never save a .3dm. Never touch C:\Users\User\Projects\bradmachado-com, the main repo, or any existing DNS record. Give explicit UI instructions (which window, menu, cell) and precede every code block with a placement instruction and a one-line intent.
Repo and versioning: work in C:\Users\User\Projects\arch575 on branch main; commit as 'section: what changed' ending with 'Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>'; tag releases as the plan says; never delete, supersede into docs/_superseded/; mirror plan and log to the OneDrive Web folder at every tag.
Portfolio capture: export process images to C:\Users\User\OneDrive - University of Illinois - Urbana\Architecture\2026 Fall - Arch 575\03_Design\05_Presentation\Web\Process named Arch575Site_S8_<Desc>_v1.0.png (environment capture + clean output image, minimum) using headless Edge where a browser capture is needed.
Gating: This subtask ends on a STOP line: STOP - report any plate or core number that changed before I continue.
On completion: append a progress-log entry (date/time, status, measured values, output files, image files, deviations, for Brad). Then, as the LAST element of your final response, output the handoff prompt for S9 copied verbatim from docs/prompts/S9_LinkIn.md with placeholders replaced by measured values, inside a single fenced code block headed 'COPY/PASTE — Prompt S9 — new conversation name: 4.9 Link In'. The first line inside the block must be the next conversation name. Nothing may follow that block.
```
