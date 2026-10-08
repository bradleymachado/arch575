# bradmachado.com — Subdomain Handoff
**Version:** 1.0 · 2026-10-08 · **Owner:** Brad Machado · **For:** the agent building `<SUB>.bradmachado.com`

Read this file in full before acting. It is the only context you have about the existing site.

---

## 0. Placeholders — fill these first

| Token | Meaning | Value |
|---|---|---|
| `<SUB>` | Subdomain label (the part before `.bradmachado.com`). Lowercase, letters/digits/hyphens. | `[BRAD TO SET]` |
| `<REPO>` | GitHub repo name for the subdomain site. Default: same as `<SUB>`. | `[BRAD TO SET]` |
| `<PROJECT>` | Human-readable project name shown on the main site. | `[BRAD TO SET]` |

If any of these is still a placeholder when you need it, ask Brad. Do not invent them.

---

## 1. Current state of bradmachado.com (verified 2026-10-08)

| Item | Value |
|---|---|
| Registrar / DNS | GoDaddy. Registered 2025-10-16, expires 2028-10-16, transfer-locked. DNS is managed at GoDaddy. |
| Hosting | GitHub Pages, account **`bradleymachado`** |
| Main site repo | `bradleymachado/bradleymachado.github.io` (public, branch `main`, folder `/ (root)`) — this is a GitHub *user site* |
| Brad's local working copy | `C:\Users\User\Projects\bradmachado-com` (Windows) |
| Stack | Hand-written static HTML + one shared stylesheet `css/style.css`. No framework, no build step, no JavaScript. |
| Apex DNS | 4 A records `@` → `185.199.108.153`, `185.199.109.153`, `185.199.110.153`, `185.199.111.153` |
| www DNS | CNAME `www` → `bradleymachado.github.io` |
| Domain verification | TXT record `_github-pages-challenge-bradleymachado` at GoDaddy. Status: **Verified** at the GitHub account level. |

**Incident history (2026-08-30):** Pages was disabled on the main repo while DNS still pointed at GitHub. A third party claimed the domain on their own Pages repo and served a gambling page at bradmachado.com. Fixed by account-level domain verification. This is why the ordering rules in Section 3 and the decommission rule in Section 8 are mandatory.

---

## 2. Architecture decision

**The subdomain is a separate GitHub repository with its own Pages site. It is not a folder in the main repo.**

- One Pages site serves exactly one custom domain. A folder in the main repo can only ever be `bradmachado.com/<folder>/`, never `<SUB>.bradmachado.com`.
- The main repo is not modified except for the link-in described in Section 6.

**Hosting constraint — check before building:**
- GitHub Pages serves static files only (HTML, CSS, JS, images, client-side apps). Static-site generators (Vite, Astro, Eleventy, etc.) are fine if built via GitHub Actions.
- If the project needs a server runtime, a database, server-side API keys, or form processing, **GitHub Pages cannot host it.** Default resolution: host on a platform that supports it (Vercel, Netlify, Cloudflare Pages + Workers) and point the `<SUB>` CNAME at that platform's target instead of GitHub. State this to Brad before proceeding; Section 3 steps 1–4 then change.

**Repo name collision rule:** because the user site has a custom domain, every Pages-enabled repo on the account is also reachable at `bradmachado.com/<REPO>/` (GitHub redirects it to the custom domain once one is set). `<REPO>` must not equal any existing top-level slug on the main site:

`about` · `brad` · `resume` · `files` · `css` · `img` · `reference` · `linea-verde-r` · `cyprus-cove` · `hub-boriken` · `less-siteless` · `artificial-context` · `hvac-rightsizing` · `aem-surveying-for-water-security` · `contextual-water-security-planning`

---

## 3. Setup procedure (GitHub Pages path)

Order matters: the repo claims the subdomain on GitHub **before** DNS points at GitHub. Never create the DNS record first.

Steps marked **[BRAD]** require a human login (GitHub web UI or GoDaddy). Steps marked **[AGENT]** you perform. At each [BRAD] step, give Brad literal, click-by-click instructions and stop until he reports the result.

1. **[BRAD] Create the repo.** github.com → **+** (top right) → **New repository** → Owner `bradleymachado`, name `<REPO>`, **Public** (Pages on a free account requires public), do **not** add a README → **Create repository**.
2. **[AGENT] Initialize and push.** In the project folder:
   - Create a file named `CNAME` at the repo root containing exactly one line: `<SUB>.bradmachado.com` (no `https://`, no trailing slash).
   - Create an empty file `.nojekyll` at the root (prevents GitHub's Jekyll processing from dropping files/folders that start with `_`).
   - Create `404.html` (see Section 5).
   - `git init`, commit, `git branch -M main`, `git remote add origin https://github.com/bradleymachado/<REPO>.git`, `git push -u origin main`. A Git Credential Manager window may appear on first push; Brad signs in.
3. **[BRAD] Enable Pages.** Repo page → **Settings** → **Pages** (left sidebar) → Build and deployment → Source: **Deploy from a branch** → Branch: **main**, folder **/ (root)** → **Save**.
   - If the project has a build step, choose Source: **GitHub Actions** instead and use the matching starter workflow; the `CNAME` file must end up in the built output folder.
4. **[BRAD] Set the custom domain on GitHub.** Same Pages page → Custom domain: `<SUB>.bradmachado.com` → **Save**. GitHub accepts it because the parent domain is verified to this account; no other account can claim it.
5. **[BRAD] Add DNS at GoDaddy.** GoDaddy → **My Products** → bradmachado.com → **DNS** → **Add New Record**:
   - Type: **CNAME** · Name/Host: `<SUB>` · Value/Points to: `bradleymachado.github.io` · TTL: default → **Save**.
   - Value is the account host only. Never include the repo name in it.
   - Do not touch any existing record. Never create a wildcard (`*`) record.
6. **[BRAD] Wait for the DNS check** on the repo's Settings → Pages page to show success (minutes to a few hours), then tick **Enforce HTTPS**.
7. **[AGENT] Verify.** `nslookup <SUB>.bradmachado.com` must return `bradleymachado.github.io` and the 185.199.108–111.153 addresses. Load `https://<SUB>.bradmachado.com` — padlock, correct content. Also confirm `https://bradmachado.com` is unchanged.

**Do not, under any circumstances:**
- Delete or edit the `_github-pages-challenge-bradleymachado` TXT record, the apex A records, or the `www` CNAME.
- Delete or edit the `CNAME` file in the main repo.
- Disable Pages on the main repo, change its branch, or push to it outside the scope of Section 6.

---

## 4. Design system (match the main site)

The subdomain should read as part of the same body of work. Austere, architectural, monochrome-plus-one-accent.

**Tokens** (copy verbatim; these are the `:root` custom properties in the main `css/style.css`):

```css
:root {
  --color-bg:          #FCFCFA; /* warm white */
  --color-ink:         #171715; /* headings, body text */
  --color-body:        #4A4A46; /* paragraph copy */
  --color-muted:       #6B6B67; /* secondary meta */
  --color-faint:       #98978F; /* captions */
  --color-hairline:    #E4E3DF; /* 1px dividers */
  --color-placeholder: #ECEBE7; /* image placeholder fill */
  --color-accent:      #B0431F; /* oxide red — the ONLY hue */
  --font-sans: "Helvetica Neue", Helvetica, Arial, sans-serif;
  --font-mono: "IBM Plex Mono", ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
  --page-max: 1440px;
  --side-margin: 72px;
  --side-margin-mobile: 24px;
  --rule-thick: 2px;
  --rule-thin: 1px;
}
```

**Rules**
- Accent `#B0431F` is the only hue. Used for: micro-labels/eyebrows, index numbers (W.01, R.01), link hover, diagram arrows, active nav item. Variation only via its tints/shades. If the project needs data-viz color, use accent tints + grays, never a second hue.
- No shadows, no rounded corners, no gradients.
- Micro-label: 11px mono, uppercase, letter-spacing 0.16em, accent color.
- Figure caption: 10px mono, uppercase, letter-spacing 0.12em, `#98978F`, format `Fig. 01 — Description.`
- Sections open with a 2px ink rule and a numbered mono title (`01 / Overview`). List rows divided by 1px hairlines.
- 72px side margins; 24px under 900px. Single column under 900px.
- IBM Plex Mono loaded from Google Fonts:
  ```html
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500&display=swap" rel="stylesheet">
  ```

**Stylesheet source:** copy (vendor) the main site's stylesheet into the subdomain repo as the baseline:
`https://raw.githubusercontent.com/bradleymachado/bradleymachado.github.io/main/css/style.css`
Do **not** hot-link `https://bradmachado.com/css/style.css` — a later change to the main site would silently break the subdomain. Add project-specific rules in a second file (e.g. `css/app.css`) rather than editing the vendored copy.

**Existing component classes** available in that stylesheet:
`container` · `section-head`, `section-head__title`, `section-head__meta` · `eyebrow` · `field-label` · `field-row`, `field-row__content` · `fig-caption` · `site-header`, `site-header__bar`, `logo`, `nav` · `hero`, `hero__title` · `spec-block` (dl of Type / Role / Tools / Status) · `figure`, `figure-grid`, `figure-pending` · `work-grid`, `project-card__image`, `project-card__heading`, `project-card__index`, `project-card__title`, `project-card__desc`, `project-card__tools` · `list-row`, `list-row__index`, `list-row__title`, `list-row__desc`, `list-row__meta` · `btn` · `diagram`, `diagram-box`, `diagram-box--dashed`, `diagram-arrow`, `diagram-label` · `site-footer` family · `page-header`, `page-header__title`, `page-header__date`, `page-header__thesis` · `next-link` · `error-page`

---

## 5. Subdomain page skeleton

**Critical:** on the subdomain, root-relative links such as `/about/` resolve to `<SUB>.bradmachado.com/about/`, which does not exist. Every link back to the main site must be **absolute**: `https://bradmachado.com/...`.

```html
<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title><PROJECT> — Brad Machado</title>
<meta name="description" content="[One sentence, Brad to verify]">
<link rel="canonical" href="https://<SUB>.bradmachado.com/">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/css/style.css">
<link rel="stylesheet" href="/css/app.css">
</head>
<body>

<header class="site-header">
  <div class="container site-header__bar">
    <a href="https://bradmachado.com/" class="logo">Brad Machado</a>
    <nav class="nav" aria-label="Primary">
      <a href="https://bradmachado.com/#work">Work</a>
      <a href="https://bradmachado.com/#research">Research</a>
      <a href="https://bradmachado.com/about/">About</a>
      <a href="https://bradmachado.com/#contact">Contact</a>
    </nav>
  </div>
</header>

<main>
  <div class="container">
    <header class="page-header">
      <span class="eyebrow">[Category] / [Index]</span>
      <div class="page-header__top">
        <h1 class="page-header__title"><PROJECT></h1>
        <span class="page-header__date">2026</span>
      </div>
      <p class="page-header__thesis">[One-sentence thesis — Brad to verify]</p>
    </header>

    <!-- project content -->
  </div>
</main>

</body>
</html>
```

`404.html` at the subdomain root: copy the main site's `404.html` pattern (eyebrow "404", title "Page not found.", `btn` link home), with absolute links as above and `<meta name="robots" content="noindex">`.

---

## 6. Linking it into bradmachado.com (main repo change)

Work in a clone of `bradleymachado/bradleymachado.github.io`. Keep the change minimal and isolated to one commit.

**Current homepage structure (`index.html`):**

| Section | id | Pattern | Entries |
|---|---|---|---|
| `01 / Selected Work` | `#work` | `work-grid` of `<article>` cards | W.01 Línea Verde R · W.02 Cyprus Cove · W.03 Hub Boriken |
| `02 / Research` | `#research` | `list-row` rows | R.01 HVAC Rightsizing · R.02 AEM Surveying · R.03 Contextual Water Security |
| `03 / Studies` | `#studies` | `work-grid` cards | S.01 Less Siteless · S.02 Artificial Context |
| Footer | `#contact` | `site-footer` | email, resume PDF, LinkedIn |

**Default placement (Brad to confirm or redirect):** a new section `04 / Development` (`id="development"`) after `#studies`, index prefix `D.` (first entry `D.01`), using the `list-row` pattern. Brad has proposed a website/app-development category for the portfolio; the exact label and position are his call.

**Row markup** (matches the existing research rows):

```html
<section id="development" aria-labelledby="development-heading">
  <div class="section-head">
    <span class="section-head__title" id="development-heading">04 / Development</span>
    <span class="section-head__meta">[Meta line — Brad to set]</span>
  </div>
  <div>
    <div class="list-row">
      <span class="list-row__index">D.01</span>
      <div>
        <a href="https://<SUB>.bradmachado.com/"><h3 class="list-row__title"><PROJECT> ↗</h3></a>
        <p class="list-row__desc">[One sentence — Brad to verify]</p>
      </div>
      <span class="list-row__meta">[Tool · Tool · Tool]</span>
    </div>
  </div>
</section>
```

**Optional case-study page on the main site** (only if Brad wants a write-up in addition to the live subdomain):
- Folder `/<slug>/index.html`, copying the structure of `cyprus-cove/index.html`: `page-header` → `spec-block` (Type / Role / Tools / Status) → figures → `01 / Process` and `02 / Outcome` `field-row`s → `next-link`.
- Stylesheet path from a subfolder page is `../css/style.css`; image paths `../img/...`.
- Images in `img/`, lowercase kebab-case, prefixed by index: `d01-<slug>-01.webp`. Convert with the repo's `optimize-images.py` (long edge ≤1800px, WebP q82; q88 for diagrams/text-heavy images — add the filename to its `HIGH_QUALITY` set).
- Every image: descriptive `alt` + mono `figcaption` (`Fig. 01 — Description.`).
- Include a `btn` linking to `https://<SUB>.bradmachado.com/` ("Open live site ↗").
- Add it to the Next Project chain: each case-study page ends in a `next-link` pointing to the next project; the current last page must be repointed to the new page, and the new page points to where the old last page pointed.

**Commit format** (both repos): `section: what changed` — e.g. `home: add D.01 <SUB> link row`. Do not commit `BUILD-PLAN.md` or `content-harvest.md` to the main repo; they are gitignored on purpose.

After pushing to the main repo: load `https://bradmachado.com` and confirm it still renders and the new link resolves. Any push to the main repo is visible publicly within ~1 minute — get Brad's approval before pushing.

---

## 7. Content rules

- **Do not invent copy.** Theses, tool lists, roles, dates, and descriptions come from Brad or his source material. Where missing, leave a `[BRACKETED]` placeholder and list it for Brad. Earlier AI-drafted copy on the main site contained false tool claims that had to be retracted.
- **Do not describe Brad as an "Army veteran" or reference "military service."** If a bio line is needed: "planner and project manager with experience in construction management, building retrofits, and design" (M.Arch candidate, Illinois School of Architecture).
- Text is terse. Images and diagrams carry the argument.
- Semantic HTML (`<nav>`, `<main>`, `<section>`, `<figure>`, `<figcaption>`). Every page needs a `<title>` (`Name — Brad Machado`), meta description, and canonical URL.
- Contact email on the main site: `bradleymachado@gmail.com`. Don't add it to new pages unless Brad asks.

---

## 8. Decommissioning (if the subdomain is ever retired or moved)

Reverse order of setup — DNS first, then GitHub:
1. **[BRAD]** Delete the `<SUB>` CNAME record at GoDaddy.
2. Wait for propagation (`nslookup <SUB>.bradmachado.com` returns no record).
3. Then disable Pages or delete the repo, and remove the link-in from the main site.

Disabling Pages while the DNS record still exists recreates the 2026-08-30 takeover condition.

---

## 9. Definition of done

- [ ] `https://<SUB>.bradmachado.com` loads over HTTPS with a padlock.
- [ ] `https://bradmachado.com` and `https://www.bradmachado.com` unchanged and working.
- [ ] Subdomain uses the tokens and type in Section 4; renders at desktop and phone width (<900px).
- [ ] All links from the subdomain back to the main site are absolute and resolve.
- [ ] Main site link-in (Section 6) merged with Brad's approval; link resolves.
- [ ] `CNAME`, `.nojekyll`, `404.html` present in the subdomain repo.
- [ ] Zero unresolved `[BRACKETED]` placeholders, or a list of them handed to Brad.
- [ ] Report to Brad: repo URL, live URL, files changed in the main repo, open placeholders.
