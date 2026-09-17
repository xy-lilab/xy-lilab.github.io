<h1 align="center">Li Lab</h1>

<p align="center">
  <strong>Xiangya Hospital · Central South University</strong><br>
  Department of Dermatology · Hunan Key Laboratory of Aging Biology
</p>

<p align="center"><strong>English</strong> · <a href="README.zh.md">简体中文</a></p>

<p align="center">
  <a href="https://github.com/xy-lilab/xy-lilab.github.io/actions/workflows/deploy.yml"><img src="https://github.com/xy-lilab/xy-lilab.github.io/actions/workflows/deploy.yml/badge.svg?branch=main" alt="Deploy site"></a>
  <a href="https://jekyllrb.com/"><img src="https://img.shields.io/badge/Jekyll-4.4-a72126?style=flat&amp;logo=jekyll&amp;logoColor=white" alt="Jekyll 4.4"></a>
  <a href="https://pages.github.com/"><img src="https://img.shields.io/badge/Hosting-GitHub%20Pages-0852a2?style=flat&amp;logo=github&amp;logoColor=white" alt="Hosted on GitHub Pages"></a>
  <a href="README.zh.md"><img src="https://img.shields.io/badge/Language-EN%20%2F%20中文-0852a2?style=flat" alt="English and Chinese"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-2e7d32?style=flat" alt="MIT License"></a>
</p>

<p align="center">
  <a href="https://www.xy-lilab.com/">Visit website</a> ·
  <a href="https://www.xy-lilab.com/research/">Research</a> ·
  <a href="https://www.xy-lilab.com/publications/">Publications</a> ·
  <a href="https://www.xy-lilab.com/people/">People</a> ·
  <a href="https://www.xy-lilab.com/join/">Join us</a>
</p>

---

## Research

The lab focuses on three major directions:

- **Rosacea and Hidradenitis Suppurativa** — pathogenesis, multi-omics, and clinical trials
- **Hair Disorders & Regeneration** — alopecia mechanisms, hair follicle biology, and regenerative strategies
- **Skin Aging** — aging mechanisms, longevity cohorts, and anti-aging interventions

## Features

- Bilingual (English / Chinese) with independent content per language
- 150+ publications with multi-dimensional filtering (direction, subtype, paper type, basic/clinical)
- Research narrative pages with inline graphical abstracts and DOI-linked citations
- Team member profiles with individual detail pages
- Automatic publication fetching from PubMed (weekly) with keyword-based classification
- Automatic citation-count refresh from OpenAlex
- Google Analytics (GA4), Open Graph / Twitter Cards, JSON-LD structured data
- Print-optimized stylesheet and responsive mobile design
- WeChat domain verification

## Tech Stack

<table align="center">
  <tr>
    <td align="center" width="100">
      <a href="https://www.ruby-lang.org/"><img src="https://skillicons.dev/icons?i=ruby&amp;theme=light" width="40" height="40" alt="Ruby"><br><sub>Ruby</sub></a>
    </td>
    <td align="center" width="100">
      <a href="https://developer.mozilla.org/docs/Web/HTML"><img src="https://skillicons.dev/icons?i=html&amp;theme=light" width="40" height="40" alt="HTML5"><br><sub>HTML5</sub></a>
    </td>
    <td align="center" width="100">
      <a href="https://developer.mozilla.org/docs/Web/CSS"><img src="https://skillicons.dev/icons?i=css&amp;theme=light" width="40" height="40" alt="CSS3"><br><sub>CSS3</sub></a>
    </td>
    <td align="center" width="100">
      <a href="https://developer.mozilla.org/docs/Web/JavaScript"><img src="https://skillicons.dev/icons?i=js&amp;theme=light" width="40" height="40" alt="JavaScript"><br><sub>JavaScript</sub></a>
    </td>
    <td align="center" width="100">
      <a href="https://www.python.org/"><img src="https://skillicons.dev/icons?i=py&amp;theme=light" width="40" height="40" alt="Python"><br><sub>Python</sub></a>
    </td>
    <td align="center" width="100">
      <a href="https://github.com/features/actions"><img src="https://skillicons.dev/icons?i=githubactions&amp;theme=light" width="40" height="40" alt="Actions"><br><sub>Actions</sub></a>
    </td>
  </tr>
</table>

- [Jekyll](https://jekyllrb.com/) 4.4 static site generator
- [Jekyll-Scholar](https://github.com/inukshuk/jekyll-scholar) for BibTeX-based publication management
- [jekyll-imagemagick](https://github.com/chrispifer/jekyll-imagemagick) for responsive WebP generation
- [GitHub Pages](https://pages.github.com/) hosting with GitHub Actions deployment
- CSS: custom design system with design tokens (no framework)
- Fonts: Merriweather, Source Serif 4, Source Sans 3, Noto Serif SC, Noto Sans SC

## Local Development

Requires Ruby 3.3+ and ImageMagick.

```bash
bundle install
bundle exec jekyll serve
# → http://127.0.0.1:4000
```

Note: first build generates hundreds of WebP thumbnails via ImageMagick and takes ~45 s. Subsequent builds with unchanged images are incremental.

## Project Structure

```
_includes/          Shared components (head, nav, footer, bib search)
_layouts/           Page templates (v2-home, v2-page, v2-people, v2-member-detail, paper-detail)
_pages/v2/          English pages
_pages/v2/zh/       Chinese pages
_data/
  members.yml       Team member profiles (bilingual, with sort_key for ordering)
  research_directions.yml  Research-direction narratives (bilingual)
  i18n/zh.yml       Chinese UI strings
_bibliography/
  papers.bib        BibTeX database (150+ entries with category/type/clinical flags)
assets/css/         v2-home.css, v2-pages.css, v2-print.css
assets/js/          v2-nav.js, bibsearch.js
assets/img/
  members/          Team member photos
  publication_preview/  Paper thumbnails (auto-resized to 480/800/1400 WebP)
  logos/            Institutional logos
scripts/
  fetch_publications.py   PubMed → bib (with auto-classification)
  classify_paper.py       Keyword-based category/type/clinical classifier
  update_citations.py     OpenAlex citation refresh
  fetch_previews.py       Paper thumbnail fetcher
.github/workflows/  CI: deploy.yml, fetch-publications.yml, update-citations.yml
.codex/skills/      Repo-local skill (governance rules for contributors)
```

## Content Management

### Adding a team member

Edit [`_data/members.yml`](_data/members.yml):

```yaml
- name: 姓名
  name_en: English Name
  sort_key: "10"           # controls order within role
  role: basic_researcher   # pi | basic_researcher | clinical_researcher | technician
  title: 研究员
  title_en: Research Fellow
  photo: /assets/img/members/xxx.jpg
  email: xxx@csu.edu.cn
  bio: >                   # paragraphs separated by <br><br>
    Line 1.<br><br>
    Line 2.
  bio_zh: >
    第一段。<br><br>
    第二段。
```

### Adding a publication

Append a BibTeX entry to [`_bibliography/papers.bib`](_bibliography/papers.bib). Required fields: `title`, `author`, `journal`, `year`, `doi`. Classification fields (`category`, `subcategory`, `publication_type`, `clinical`, `basic`) drive the filtering UI on `/publications/`.

Alternatively, let the automation do it — the PubMed fetch workflow (weekly) auto-appends new papers with classification.

### Editing research narratives

Edit [`_data/research_directions.yml`](_data/research_directions.yml) — each entry has `intro` / `intro_zh` (bullet list for homepage) and `narrative` / `narrative_zh` (long-form for detail page).

## Automation

Three scheduled workflows keep data fresh without manual work:

| Workflow | Schedule | What it does |
| --- | --- | --- |
| `deploy.yml` | on push | Builds Jekyll site, caches ImageMagick WebP output, deploys to gh-pages |
| `fetch-publications.yml` | weekly | Queries PubMed for new lab papers, appends classified entries to papers.bib |
| `update-citations.yml` | weekly | Refreshes `citation_count` from OpenAlex |

## Design

- **Colors**: Xiangya Red (`#a72126`) + CSU Blue (`#0852a2`)
- **Typography**: serif titles (Merriweather) + serif body (Source Serif 4) + sans UI (Source Sans 3)
- **Chinese typography**: Noto Serif SC (titles) + Noto Sans SC (body), justified text with first-line indent for PI/member bios
- **Design tokens**: all colors, fonts, spacing managed via CSS variables in `v2-home.css`
- **Academic niceties**: oldstyle numerals, automatic hyphenation, orphan/widow control

## Governance

Repository-specific rules for contributors (including AI assistants) live in [`AGENTS.md`](AGENTS.md) and [`.codex/skills/xy-lilab-site-governance/`](.codex/skills/xy-lilab-site-governance/). Read these before making structural changes.

## License

[MIT](LICENSE)
