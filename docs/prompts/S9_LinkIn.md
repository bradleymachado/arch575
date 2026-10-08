# Prompt S9 — Link In

Copy everything inside the fence into a new conversation (or hand it to the `cs-exec-medium` agent).

```
4.9 Link In
Name this conversation exactly '4.9 Link In'. Your first response must begin with the line: CONVERSATION NAME: 4.9 Link In.
Model tier: cs-exec-medium (Opus). (If run from the orchestrator session, spawn with that cs-exec agent type.)
Project: arch575.bradmachado.com web presentation — ARCH 575, Fall 2026. Execute subtask S9 only: Main-site link-in (04 / Development, D.01) - post-review, only on Brad's instruction.
First read C:\Users\User\Projects\arch575\docs\Arch575Site_Plan_v1.1.md (plan §3 rules and §4 S9 steps) and the progress log C:\Users\User\Projects\arch575\docs\Arch575Site_ProgressLog_v1.0.md. Do not re-plan; follow the subtask steps as written. Also read docs/reference/Arch575Site_Handoff_v1.0.md and docs/reference/Subdomain_Handoff_v1.0.md in the repo when the steps cite them.
Inputs: Subdomain handoff §6 verbatim; a fresh clone of bradleymachado/bradleymachado.github.io in a scratch folder (not Brad's working copy); [Meta line], [One sentence], [Tool · Tool · Tool] are Brad's to supply - do not invent.
Time budget: 15 min. Required outputs: One commit 'home: add D.01 arch575 link row' in the clone, NOT pushed; diff shown to Brad.
Acceptance checks: Diff touches only index.html; all links absolute; after Brad's explicit approval and push, https://bradmachado.com renders and the new row resolves.
Tooling rules: GitHub Pages (public repo bradleymachado/arch575, branch main, root); static HTML + CSS + ES-module JS; three.js 0.186.1 vendored into js/vendor/ (no CDN at runtime); Python 3.10.11 for build scripts (rhino3dm 8.35.0, matplotlib 3.10.9, python-pptx, Markdown); git + gh CLI (logged in as bradleymachado); headless Edge for captures; no Node, no build step, no Chrome/computer-use automation while Brad is at the machine; Microsoft Office only; no Google products. Never save a .3dm. Never touch C:\Users\User\Projects\bradmachado-com, the main repo, or any existing DNS record. Give explicit UI instructions (which window, menu, cell) and precede every code block with a placement instruction and a one-line intent.
Repo and versioning: work in C:\Users\User\Projects\arch575 on branch main; commit as 'section: what changed' ending with 'Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>'; tag releases as the plan says; never delete, supersede into docs/_superseded/; mirror plan and log to the OneDrive Web folder at every tag.
Portfolio capture: export process images to C:\Users\User\OneDrive - University of Illinois - Urbana\Architecture\2026 Fall - Arch 575\03_Design\05_Presentation\Web\Process named Arch575Site_S9_<Desc>_v1.0.png (environment capture + clean output image, minimum) using headless Edge where a browser capture is needed.
Gating: This subtask ends on a STOP line before any push: STOP - report approval to push the one-commit diff shown above before I continue.
On completion: append a progress-log entry (date/time, status, measured values, output files, image files, deviations, for Brad). Then, as the LAST element of your final response, output a 'COPY/PASTE — Project closeout' block: final values, files delivered, tags, open items. Nothing may follow that block.
```
