# Prompt S6 — Review

Copy everything inside the fence into a new conversation (or hand it to the `cs-exec-high` agent).

```
4.6 Review
Name this conversation exactly '4.6 Review'. Your first response must begin with the line: CONVERSATION NAME: 4.6 Review.
Model tier: cs-exec-high (Opus). (If run from the orchestrator session, spawn with that cs-exec agent type.)
Project: arch575.bradmachado.com web presentation — ARCH 575, Fall 2026. Execute subtask S6 only: Review against the handoffs, numbers, captures, copy status.
First read C:\Users\User\Projects\arch575\docs\Arch575Site_Plan_v1.2.md (plan §3 rules and §4 S6 steps) and the progress log C:\Users\User\Projects\arch575\docs\Arch575Site_ProgressLog_v1.0.md. Do not re-plan; follow the subtask steps as written. Also read docs/reference/Arch575Site_Handoff_v1.0.md and docs/reference/Subdomain_Handoff_v1.0.md in the repo when the steps cite them.
Inputs: Site handoff §2 and §9; subdomain handoff §4 and §9; plan §1 numbers; copy status table in the log; the site at http://localhost:8000.
Time budget: 20 min. Required outputs: Pass/fail table in the log; 24 captures (12 slides x 2 widths) in C:\Users\User\OneDrive - University of Illinois - Urbana\Architecture\2026 Fall - Arch 575\03_Design\05_Presentation\Web\Process; one-line fixes committed as 'review: fixes'; list of remaining items for S7 / Brad.
Acceptance checks: All rows pass or are assigned; the number diff script reports 0 mismatches; no [BRACKETS] visible; accent is the only hue in computed styles (sample 5 elements); hotel elevator no-stop symbols present on L18-L32.
Tooling rules: GitHub Pages (public repo bradleymachado/arch575, branch main, root); static HTML + CSS + ES-module JS; three.js 0.186.1 vendored into js/vendor/ (no CDN at runtime); Python 3.10.11 for build scripts (rhino3dm 8.35.0, matplotlib 3.10.9, python-pptx, Markdown); git + gh CLI (logged in as bradleymachado); headless Edge for captures; no Node, no build step, no Chrome/computer-use automation while Brad is at the machine; Microsoft Office only; no Google products. Never save a .3dm. Never touch C:\Users\User\Projects\bradmachado-com, the main repo, or any existing DNS record. Give explicit UI instructions (which window, menu, cell) and precede every code block with a placement instruction and a one-line intent.
Repo and versioning: work in C:\Users\User\Projects\arch575 on branch main; commit as 'section: what changed' ending with 'Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>'; tag releases as the plan says; never delete, supersede into docs/_superseded/; mirror plan and log to the OneDrive Web folder at every tag.
Portfolio capture: export process images to C:\Users\User\OneDrive - University of Illinois - Urbana\Architecture\2026 Fall - Arch 575\03_Design\05_Presentation\Web\Process named Arch575Site_S6_<Desc>_v1.0.png (environment capture + clean output image, minimum) using headless Edge where a browser capture is needed.
Gating: This subtask ends on a STOP line. List the unconfirmed copy lines, then end with: STOP - report confirmation of the copy lines listed, or your edits, before I continue.
On completion: append a progress-log entry (date/time, status, measured values, output files, image files, deviations, for Brad). Then, as the LAST element of your final response, output the handoff prompt for S7 copied verbatim from docs/prompts/S7_DeployLog.md with placeholders replaced by measured values, inside a single fenced code block headed 'COPY/PASTE — Prompt S7 — new conversation name: 4.7 Deploy Log'. The first line inside the block must be the next conversation name. Nothing may follow that block.
```
