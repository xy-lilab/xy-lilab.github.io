# Design Philosophy

## Product Posture

- This site is an academic institution site, not a startup landing page.
- The default tone is credible, calm, and translational rather than promotional.
- Visual choices should reinforce scientific seriousness, institutional trust, and readability.
- High-value content should appear before decorative flourishes.
- The site must be legible to international visitors who may know neither Xiangya Hospital nor the Chinese academic system in advance, as well as to domestic visitors reading the Chinese mirror.
- Lean toward a strong institutional / editorial feel rather than a design-forward SaaS landing page.
- The homepage may lean toward a sparse, quiet academic-portfolio cadence as long as it remains clearly institutional.

## Narrative Priorities

- Lead with the lab's bridge between clinical dermatology and molecular biology.
- Keep the three flagship research directions visible and stable:
  - rosacea and hidradenitis suppurativa
  - hair disorders and hair regeneration
  - skin aging
- Support the research story with publications, team credibility, and clinical context.
- Recruiting and contact should be easy to find, but should not overpower the research narrative.
- Do not let the homepage say the same thing twice in slightly different wording. If the research-direction block already carries the three directions, the surrounding paragraphs should add institutional or methodological context instead of restating the same list.

## Visual System

### Colors

- Primary: Xiangya Red (`#a72126`) and CSU Blue (`#0852a2`).
- Ink, muted ink, background, and hairline tones are driven by CSS custom properties declared at the top of `assets/css/v2-home.css`. Prefer editing those tokens over introducing new hex values.
- Color changes must preserve academic tone and sufficient contrast. Avoid turning the site into a generic tech-brand palette.

### Typography

- English display and headings: `Merriweather` (serif).
- English body: `Source Serif 4` (serif).
- English UI, nav, and small labels: `Source Sans 3` (sans).
- Chinese titles: `Noto Serif SC` (with fallbacks to `Songti SC`, `STSong`).
- Chinese body: `Noto Sans SC`.
- Chinese body copy for PI and member bios uses `text-align: justify` with a first-line indent.
- Academic niceties that should be preserved: oldstyle numerals, automatic hyphenation, and orphan/widow control.
- Typography changes must preserve legibility on desktop and mobile.
- Do not introduce opportunistic font swaps for a single page or component.

### Layout and Hierarchy

- Hierarchy should come primarily from scale, spacing, alignment, and contrast, not from multiplying cards, labels, or decorative containers.
- On interior pages, section and program headings must sit clearly below the page title on both desktop and mobile.
- Keep the number of major homepage sections low enough that the page can be scanned in one pass.
- Mobile should not be a desktop layout with narrower width. Tighten chrome, type scale, and vertical rhythm deliberately for phone-sized screens.
- Avoid glassmorphism, oversized pill treatments, loud background textures, and large-radius card stacks when they make the site feel ornamental instead of institutional.
- Prefer quieter page planes, sharper hierarchy, restrained accents, and a more paper-like or editorial sense of structure.
- Avoid using heavy shadows, thick borders, or card stacks to compensate for weak typographic hierarchy.

### Motion

- Motion should support emphasis, orientation, or polish.
- Avoid decorative animation that competes with scientific content.

### Imagery

- Keep imagery relevant to research areas, publications, or institutional identity.
- Publication preview images must flow through `jekyll-imagemagick` responsive WebP generation; do not bypass it for one-off thumbnails.
- Research-direction images should display fully rather than being aggressively cropped inside cards.

## Content Strategy

- Repeated scientific statements should come from data/content files (`_data/research_directions.yml`, `_data/members.yml`, `_bibliography/papers.bib`) rather than from multiple disconnected layout fragments.
- Prefer short, concrete, literal copy over abstract framing language.
- Avoid meta-writing about the website itself when a direct statement about the lab, the research, or the opportunity would be clearer.
- Avoid stacking multiple high-level abstractions in one paragraph; readers should understand the sentence on the first pass.
- Homepage copy should explain the lab in one short headline and a short supporting paragraph before moving into research, publications, team, or contact.
- Do not add a new explanatory section if an existing section already covers the same claim.
- International-facing copy should prefer globally legible academic language over institution-internal phrasing or translated bureaucratic wording.
- Domestic Chinese copy should read as native Chinese, not as a literal translation from English.
- If a homepage preview cannot feel complete, remove it and rely on the dedicated interior page instead.

## Bilingual Strategy

- The public surface is bilingual: `/` is English and `/zh/` is Chinese.
- English and Chinese content are independent at the copy level but semantically aligned: both languages must cover the same sections, same research directions, and same team.
- Shared UI strings live in `_data/i18n/en.yml` and `_data/i18n/zh.yml`. Do not hardcode UI strings in layouts when the i18n data file already carries them.
- Bilingual fields on `_data/members.yml` (`name`/`name_en`, `title`/`title_en`, `bio`/`bio_zh`) and `_data/research_directions.yml` (`intro`/`intro_zh`, `narrative`/`narrative_zh`) are the source of truth.
- A structural design change that affects one language must also be applied to the other language unless the user explicitly scopes the change to one side and the skill is updated to record the asymmetry.
- Do not silently expand or shrink bilingual coverage.

## Navigation and Chrome

- Keep the primary navigation small and stable across both languages.
- The visible nav brand should read as compact site chrome, not as a second headline competing with the page title.
- On phone-sized screens, navigation menus must be truly hidden when closed. The toggle should be the only visible control until the menu opens.
- The footer should stay quiet and utilitarian. Do not repeat the homepage research-direction summary in the footer.
- Do not duplicate active header-navigation destinations in the footer just to fill space.

## Publications Presentation

- Publications are a core credibility feature, not a secondary archive.
- Publication lists should prioritize scanning by title, authors, venue, year, and detail link. Preview thumbnails are optional; the dedicated Publications pages and the Clinical pages' embedded publication lists stay text-only where image coverage is sparse.
- Detail pages should stay content-first and easy to read. Prefer a simple bibliographic header over dashboard-like metadata boxes.
- Filter UI on `/publications/` is driven by classification fields in `_bibliography/papers.bib` (`category`, `subcategory`, `publication_type`, `clinical`, `basic`). Do not invent new filter facets without updating the skill first.
- Changes to bibliography rendering or paper-detail UX require a skill update first.

## Team Presentation

- The team page should read like a calm people directory, not a gallery wall.
- PI block is visually distinct from grouped member listings.
- Secondary member portraits stay modest; headshots support recognition rather than dominating the page.
- Role groupings come from the existing member taxonomy (`pi`, `basic_researcher`, `clinical_researcher`, `technician`) and should not be changed casually.
- `sort_key` inside `_data/members.yml` controls order within each role; prefer adjusting `sort_key` over re-ordering list entries.
- Long biography belongs in `bio`/`bio_zh`; keep PI summary on the homepage short.

## Final-Polish Priorities

- For final-quality homepage and interior pages, prioritize in this order:
  - rhythm
  - restraint
  - hierarchy
  - recognizability on first glance
- Do not chase impact by adding modules. The page becomes more striking when each remaining element has a clear visual job.
