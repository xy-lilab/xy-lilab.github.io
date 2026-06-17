# Feature Design

## Site-Level Goals

- Help visitors understand what the lab studies, why it matters, and who is doing the work.
- Make publications and research directions discoverable in a small number of clicks.
- Keep content maintenance straightforward for a Jekyll-based static site.
- Prioritize fast comprehension for both international academic visitors (English surface) and domestic visitors (Chinese surface) over exhaustive explanation.

## Page Intent

### Home (`/` and `/zh/`)

- Explain the lab's positioning quickly: clinical dermatology + molecular biology, based at Xiangya Hospital.
- Surface the three research directions with concrete scientific substance, not abstract framing.
- Reinforce credibility with featured publications and institutional anchor.
- The homepage should resolve into four jobs:
  - establish the lab and its institution
  - show the three research directions (with inline citations to flagship papers)
  - show representative publications
  - route to team, clinical, careers, or contact
- Each homepage section should help the visitor act or understand something specific. Remove sections that do not change understanding or navigation.
- The PI introduction belongs on the homepage. Keep it short on the homepage and let the team page carry the fuller profile.
- Research-direction narratives on the homepage come from `_data/research_directions.yml`'s `intro` / `intro_zh` fields (the bullet-list summary). The longer `narrative` / `narrative_zh` is reserved for the detail page.

### Research Direction Detail Pages

- Each research direction has a dedicated detail page backed by `_data/research_directions.yml`.
- The research taxonomy must stay stable unless the lab's scientific framing changes. Changing the taxonomy requires a skill update first.
- Detail pages should connect the narrative summary to bibliography-driven evidence: inline DOI links, graphical abstracts, and representative papers.
- Prefer concrete scientific claims (genes, pathways, trial endpoints) over abstract framing.

### Publications (`/publications/` and `/zh/publications/`)

- Publications are a core credibility feature, not a secondary archive.
- The list page supports multi-dimensional filtering driven by bib fields: research direction (`category`), subtype (`subcategory`), paper type (`publication_type`), and clinical/basic flags.
- The list page should support scanning by title, authors, venue, year, and preview thumbnail.
- Detail pages should stay reading-first: title, authors, venue / year / DOI, outward publisher link, abstract, and the graphical abstract when available.
- Do not introduce card-heavy metadata dashboards on detail pages.
- Any change to the filter facets, list rendering, or detail layout requires a skill update first.

### Team (`/people/` and `/zh/people/`)

- Team page emphasizes people as research contributors, not generic profile cards.
- PI block is visually distinct from grouped member listings.
- Role grouping follows `_data/members.yml`'s `role` taxonomy (`pi`, `basic_researcher`, `clinical_researcher`, `technician`). Order inside each group is controlled by `sort_key`.
- Member detail pages (`/people/<slug>/` and `/zh/people/<slug>/`) carry longer bio, photo, contact, and selected publications where applicable.
- For members without a photo, keep the roster compact rather than forcing placeholder-style empty-image blocks.

### Clinical (`/clinical/` and `/zh/clinical/`)

- Explain how the lab's science translates into real clinical programs and resources.
- Keep this page focused on translational value rather than duplicating the entire research page.
- Prefer concrete research/clinical interfaces — cohorts, sample collections, disease focus, therapeutic questions, trial routes — over abstract language about translation.
- Usually resolves to: current interfaces + one contact / collaboration route.

### Contact (`/contact/` and `/zh/contact/`)

- Lightweight contact reference: lab emails, postal address (Department of Dermatology, Xiangya Hospital), map link, and online profiles.
- Keep it a fast lookup surface; do not let it absorb recruiting content. Point applicants to Join Us instead.
- Backed by `_pages/v2/contact.md` and `_pages/v2/zh/contact.md`.

### Join Us (`/join/` and `/zh/join/`)

- Dedicated recruiting page — English "Join Us" / Chinese "加入我们" — surfaced in primary navigation.
- Reads as a direct recruiting note: open positions, who should apply, how to apply, one clear application route.
- Positions track the lab's actual openings (faculty-scientist / PI-track, postdoc, technician); each block states eligibility and compensation. When the lab publishes salary figures, list them concretely.
- Preserve an academically serious tone; avoid generic corporate recruiting language. Do not repeat role philosophy and application instructions in multiple sections.
- Do NOT duplicate PI / co-PI bios or research-direction descriptions; link to People and Research instead.
- Backed by `_pages/v2/join.md` and `_pages/v2/zh/join.md`.

> History: `_pages/v2/careers.md` / `_pages/v2/zh/careers.md` were repurposed into the Contact page and have been renamed to `contact.md`. Recruiting now lives on the dedicated Join Us page above, not on Contact.

### Projects (`/research/` and `/zh/research/`)

- Lightweight research-project overview, complementary to the research-direction detail pages.
- Should not duplicate the homepage research-direction narrative; use it for additional programs or translational initiatives when needed.

### 404

- Simple not-found page; no marketing content.

## Navigation

- Primary navigation is small and stable across both languages. Current order: Home · Research · Publications · People · Clinical · Join Us · Contact (with the language switcher).
- Navigation labels are hard-coded in `_includes/nav.liquid` (the `nav:` keys in `_data/i18n/*.yml` are legacy and currently unused).
- The language switcher must be visible on every page and must send the user to the semantically matching page in the other language, not to the `/` or `/zh/` root.
- Navigation taxonomy changes require a skill update first.

## Publication Automation

- `fetch-publications.yml` runs weekly: `scripts/fetch_publications.py` queries PubMed for new lab papers, classifies them via `scripts/classify_paper.py`, and appends BibTeX entries to `_bibliography/papers.bib`.
- `update-citations.yml` runs weekly: `scripts/update_citations.py` refreshes `citation_count` from OpenAlex into `_data/citations.yml`.
- The keyword-based classifier is the current source of truth for category / subcategory / publication-type / clinical / basic assignment. Manual edits to those fields in `papers.bib` should only override the classifier when the classifier is wrong; do not fight the automation by resetting fields each run.
- Changes to the fetch cadence, the classification schema, or the source-of-truth for citation counts require a skill update first.

## Build and Deploy

- `deploy.yml` runs on push to main: builds Jekyll, caches ImageMagick WebP output and apt-installed ImageMagick, deploys to `gh-pages`.
- First build generates several hundred WebP thumbnails via `jekyll-imagemagick`; subsequent builds reuse the WebP cache.
- Do not bypass `jekyll-imagemagick` for publication previews — add the source image to `assets/img/publication_preview/` and let the plugin generate responsive WebP.

## Analytics, SEO, Sharing

- Google Analytics 4 snippet, Open Graph / Twitter Card meta tags, and JSON-LD structured data are wired through `_includes/head.liquid` and `_layouts/v2.liquid`.
- Removing or changing any of these touches every page. Treat as a site-level change and update the skill first.

## Bilingual Expectations

- Adding a new core page or changing page purpose requires updating the `/zh/` counterpart or the shared i18n strings.
- If a change is intentionally one-language-only, make that explicit in the skill before the asymmetry becomes a precedent.

## New Feature Checklist

- Identify the source of truth:
  - page front matter (`_pages/v2/*` or `_pages/v2/zh/*`)
  - `_data/*.yml`
  - `_bibliography/papers.bib`
  - i18n strings (`_data/i18n/*.yml`)
  - layout-only presentation logic (rare)
- Decide whether the change affects navigation, bilingual coverage, publication rendering, team taxonomy, or research-direction taxonomy. If yes, update the skill first.
- Prefer editing data/content files over editing layouts.
- Prefer extending an existing layout over introducing a new one. If a new layout is required, document its ownership in `module-map.md` at the same time.

## Avoid

- Hiding scientific substance behind oversized interface treatments.
- Putting structured content into layout files when a data or content file is the better source of truth.
- Introducing a new build dependency, plugin, or client framework as an incidental implementation choice.
- Adding fact rails, stat grids, or dashboard-style tiles to pages whose content does not require them.
