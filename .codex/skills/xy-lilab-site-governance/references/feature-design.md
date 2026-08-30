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
- The list is text-only — scan by title, authors, venue, and year. Preview thumbnails are intentionally off (`hide_publication_thumbnails: true` on both publications pages): most entries lack an image, so the featured block hides thumbs via CSS and the complete list matches. Citation counts live in `_data/citations.yml` but are hidden site-wide via CSS (`.bib-citation-badge { display: none }`), so they are not a visible list field.
- Detail pages should stay reading-first: title, authors, venue / year / DOI, outward publisher link, abstract, and the graphical abstract when available.
- Show `Read more` only when the bibliography entry contains an abstract. Papers whose authoritative metadata has no abstract still link outward through the title/DOI; do not send visitors to a detail page that adds no substantive content, and never fabricate a replacement abstract.
- An `abstract` must be a genuine scholarly abstract. Letter body text, correction/erratum notices, data-availability statements, publisher disclaimers, editorial body text, affiliations, and other indexing fragments are invalid and must not be stored or rendered as abstracts.
- Correction, erratum, and corrigendum records are bibliographic maintenance notices rather than research outputs. They must not be stored in the website's `papers.bib`, because jekyll-scholar would still generate detail routes for hidden entries; automated fetch skips them before append.
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
- The embedded related-publications list is text-only in both languages (`hide_publication_thumbnails: true` in both Clinical page front matters), matching the dedicated Publications pages and avoiding a patchy list when preview coverage is incomplete.
- Usually resolves to: current interfaces + one contact / collaboration route.

### Contact (`/contact/` and `/zh/contact/`)

- Lightweight contact reference: lab emails, postal address (Department of Dermatology, Xiangya Hospital), map link, and online profiles.
- Keep it a fast lookup surface; do not let it absorb recruiting content. Point applicants to Join Us instead.
- The contact details sit on the left beside a team group photo on the right (`page_class: contact` keys a scoped `.v2-contact-grid`; stacks to one column ≤768px, photo below the details). The photo is the only visual flourish here — keep it a single image (`assets/img/lab_team.jpg`), not a gallery, so the page stays a fast lookup surface. Like the Join page, the details column is authored as literal HTML inside the grid's raw-HTML block (Kramdown does not parse Markdown there); Liquid still runs (the Online block is conditional on `_data/socials.yml`).
- Backed by `_pages/v2/contact.md` and `_pages/v2/zh/contact.md`.

### Join Us (`/join/` and `/zh/join/`)

- Dedicated recruiting page — English "Join Us" / Chinese "加入我们" — surfaced in primary navigation.
- Reads as a direct recruiting note: open positions, who should apply, how to apply, one clear application route.
- The page covers two distinct recruiting tracks, kept as separate clearly-headed sections so employment and degree-seeking applicants are not conflated:
  - **Paid staff / faculty positions (招聘)** — the lab's actual openings (faculty-scientist / PI-track, postdoc, technician); each block states eligibility and compensation. When the lab publishes salary figures, list them concretely. This track carries the formal application instructions (materials, recommendation letters).
  - **Graduate-student admissions (招生)** — master's and doctoral students. Per Xiangya Hospital policy, master's admission is restricted to clinical-medicine majors; doctoral admission is open to clinical-medicine or biomedicine-related fields. State these major constraints explicitly. There are no special prerequisites beyond the major requirement; keep the student application route light (email a CV to the PIs) and note that formal enrolment follows Central South University's annual graduate-admissions process. Do not impose the staff track's publication/recommendation-letter requirements on students.
- Preserve an academically serious tone; avoid generic corporate recruiting language. Do not repeat role philosophy and application instructions in multiple sections.
- Do NOT duplicate PI / co-PI bios or research-direction descriptions; link to People and Research instead.
- The two tracks render side by side as two columns (`.v2-join-grid` > two `.v2-join-col`), 招聘 on the left and 招生 on the right, parted by a single vertical hairline. On narrow viewports (≤768px, matching the homepage direction grid) they stack to one column and the parting rule becomes horizontal. The lab-wide intro paragraph spans full width above the grid; the "More about the lab" footer line (with its `<hr>`) spans full width below. The staff column is the taller of the two (it carries the role list plus the eligibility and how-to-apply detail); the columns top-align and the shorter admissions column simply ends earlier — do not pad it out with filler to force equal height. Because the columns live inside one raw-HTML block, the staff column's "Eligibility and platform" / "How to apply" subsections and the admissions note are authored as literal HTML (`<h3>`, `<ul>`, `<p>`), not Markdown — Kramdown does not parse Markdown inside block HTML here. Kramdown's smart-quote/dash typography also does not run inside this raw HTML, so type literal typographic glyphs directly (curly “ ” ‘ ’, en-dash –) rather than relying on `"`/`'`/`--` being converted; the Chinese page already uses full-width quotes, so this only matters on the English page.
- Each track opens with the shared `.v2-section__intro` accent-underlined `<h2>` header (the same accent-header component used on Clinical / Publications, used standalone without the `.v2-section` wrapper). The headers stand alone with no descriptive sub-line.
- The page carries `page_class: join`, which keys a small scoped block in `v2-pages.css`: the two-column grid + vertical divider, an enlarged track `<h2>`, and a hairline bottom rule on the staff column's in-track sub-section `<h3>`s (`.v2-join-col > h3`) so the tiers (page title › red-underlined track header › hairline-ruled sub-section › serif role title) read clearly. Keep this scoped to the Join page; do not push these sizes onto the shared interior-page heading rules. Rely on this accent-header + hairline rhythm for separation; do not introduce heavy dividers, boxes, or cards (see design-philosophy: hierarchy from scale/spacing/contrast, not containers).
- Both tracks render as the same editorial role list (`.v2-role*`): hairline-separated blocks, role title with a sans accent (`.v2-role__pay` — the headline salary for staff positions; the required major for graduate roles), then a label/value `<dl>`. Staff blocks use Who / Background / Bar / Package; graduate blocks use a lighter Eligibility / Looking-for pair. Do not revert to boxed `v2-utility-card`s — the per-role detail is too dense for the card grid.
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

- `fetch-publications.yml` runs weekly: `scripts/fetch_publications.py` first backfills missing abstracts on existing entries, then queries PubMed for new lab papers, classifies them via `scripts/classify_paper.py`, and appends BibTeX entries to `_bibliography/papers.bib`.
- Abstract source priority is PubMed, then PMC for PubMed-linked open full text, OpenAlex by DOI, and finally a batched Semantic Scholar DOI lookup. PubMed structured abstracts must join all labelled `AbstractText` sections. Every source passes a content-level rejection check for correction notices, letter/editorial body text, data-availability boilerplate, and publisher disclaimers. Secondary-index fallback is additionally disabled for letters, editorials, corrections, or case reports. Newly fetched correction records are skipped before append. A missing valid upstream abstract remains missing rather than being inferred or generated.
- `update-citations.yml` runs weekly: `scripts/update_citations.py` refreshes `citation_count` from OpenAlex into `_data/citations.yml`.
- The keyword-based classifier is the current source of truth for category / subcategory / publication-type / clinical / basic assignment. Manual edits to those fields in `papers.bib` should only override the classifier when the classifier is wrong; do not fight the automation by resetting fields each run.
- Impact factor + JCR quartile are sourced from a committed Clarivate JCR export (`scripts/data/jcr_2025.json`) via `scripts/jcr_lookup.py` — used by both the weekly fetch (new papers) and `scripts/refresh_impact_factors.py` (bulk re-run). When a new JCR table arrives: drop the `.xlsx`, run `build_jcr_data.py` to regenerate the JSON, then `refresh_impact_factors.py --apply`. The `cas_quartile` (中科院分区) field has been retired — never displayed, not maintained.
- Changes to the fetch cadence, the classification schema, the impact-factor data source, or the source-of-truth for citation counts require a skill update first.

## Build and Deploy

- `deploy.yml` runs on push/PR to main, manual dispatch, and on `workflow_run` completion of `Fetch new publications` (the weekly paper fetch). A lightweight `gate` job builds only when that run produced a new commit (branch tip != `workflow_run.head_sha`), so empty fetch weeks do not redeploy. `Update citation counts` deliberately does NOT trigger deploy — citation counts are hidden site-wide via CSS, so rebuilding for them has no visible effect; refreshed counts ride along on the next fetch/human deploy. The build itself: Jekyll build, caches ImageMagick WebP output and apt-installed ImageMagick, deploys to `gh-pages`.
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
