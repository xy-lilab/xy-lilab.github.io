<p align="center">
  <a href="https://www.xy-lilab.com/zh/"><img src="https://capsule-render.vercel.app/api?type=waving&amp;color=0%3A0852a2%2C100%3Aa72126&amp;height=200&amp;section=header&amp;text=Li+Lab&amp;fontFamily=Georgia&amp;fontSize=64&amp;fontColor=ffffff&amp;fontAlignY=37&amp;desc=Dermatology+%C2%B7+Molecular+Biology&amp;descSize=19&amp;descAlignY=59" alt="Li Lab — Dermatology and Molecular Biology" width="100%"></a>
</p>

<p align="center">
  <strong>中南大学湘雅医院 · Li 实验室</strong><br>
  衰老生物学湖南省重点实验室 · 皮肤科
</p>

<p align="center"><a href="README.md">English</a> · <strong>简体中文</strong></p>

<p align="center">
  <a href="https://github.com/xy-lilab/xy-lilab.github.io/actions/workflows/deploy.yml"><img src="https://github.com/xy-lilab/xy-lilab.github.io/actions/workflows/deploy.yml/badge.svg?branch=main" alt="Deploy site"></a>
  <a href="https://jekyllrb.com/"><img src="https://img.shields.io/badge/Jekyll-4.4-a72126?style=flat-square&amp;logo=jekyll&amp;logoColor=white" alt="Jekyll 4.4"></a>
  <a href="https://pages.github.com/"><img src="https://img.shields.io/badge/Hosting-GitHub%20Pages-0852a2?style=flat-square&amp;logo=github&amp;logoColor=white" alt="Hosted on GitHub Pages"></a>
  <a href="README.md"><img src="https://img.shields.io/badge/Language-EN%20%2F%20中文-0852a2?style=flat-square" alt="English and Chinese"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-555555?style=flat-square" alt="MIT License"></a>
</p>

<p align="center">
  <img src="https://readme-typing-svg.demolab.com?font=Noto+Sans+SC&amp;size=21&amp;duration=2800&amp;pause=2200&amp;color=A72126&amp;center=true&amp;vCenter=true&amp;width=760&amp;height=44&amp;lines=%E7%8E%AB%E7%91%B0%E7%97%A4%E7%96%AE%E4%B8%8E%E5%8C%96%E8%84%93%E6%80%A7%E6%B1%97%E8%85%BA%E7%82%8E%3B%E6%AF%9B%E5%8F%91%E7%96%BE%E7%97%85%E4%B8%8E%E5%86%8D%E7%94%9F%3B%E7%9A%AE%E8%82%A4%E8%A1%B0%E8%80%81" alt="玫瑰痤疮与化脓性汗腺炎 · 毛发疾病与再生 · 皮肤衰老">
</p>

<p align="center">
  <a href="https://www.xy-lilab.com/zh/">访问网站</a> ·
  <a href="https://www.xy-lilab.com/zh/research/">研究方向</a> ·
  <a href="https://www.xy-lilab.com/zh/publications/">学术论文</a> ·
  <a href="https://www.xy-lilab.com/zh/people/">研究团队</a> ·
  <a href="https://www.xy-lilab.com/zh/join/">加入我们</a>
</p>

---

## 研究方向

实验室聚焦三大研究方向：

- **玫瑰痤疮与化脓性汗腺炎** — 发病机制、多组学、临床试验
- **毛发疾病与再生** — 脱发机制、毛囊生物学、再生策略
- **皮肤衰老** — 衰老机制、长寿队列、抗衰干预

## 功能特性

- 中英双语独立内容（`/` 英文，`/zh/` 中文）
- 150+ 篇论文，多维度筛选（研究方向、亚型、论文类型、基础/临床）
- 研究方向详情页，内嵌图形摘要与 DOI 引用
- 团队成员资料与独立详情页
- 每周自动从 PubMed 抓取新论文并基于关键词自动分类
- 每周自动从 OpenAlex 刷新引用数
- Google Analytics (GA4)、Open Graph / Twitter Cards、JSON-LD 结构化数据
- 打印样式优化，移动端响应式
- 微信域名校验

## 技术栈

<p>
  <img src="https://skillicons.dev/icons?i=ruby,html,css,js,py,githubactions&amp;theme=light" alt="Ruby、HTML、CSS、JavaScript、Python、GitHub Actions" height="48">
</p>

- [Jekyll](https://jekyllrb.com/) 4.4 静态站点生成器
- [Jekyll-Scholar](https://github.com/inukshuk/jekyll-scholar) — 基于 BibTeX 的论文管理
- [jekyll-imagemagick](https://github.com/chrispifer/jekyll-imagemagick) — 自动生成响应式 WebP
- [GitHub Pages](https://pages.github.com/) 托管 + GitHub Actions 部署
- CSS：自建设计令牌系统（不用框架）
- 字体：Merriweather、Source Serif 4、Source Sans 3、Noto Serif SC、Noto Sans SC

## 本地开发

需要 Ruby 3.3+ 与 ImageMagick。

```bash
bundle install
bundle exec jekyll serve
# → http://127.0.0.1:4000
```

说明：首次构建会通过 ImageMagick 生成数百张 WebP 缩略图，约 45 秒；后续图片未变动时增量构建。

## 项目结构

```
_includes/          公共组件（head、nav、footer、bib 搜索）
_layouts/           页面模板（v2-home、v2-page、v2-people、v2-member-detail、paper-detail）
_pages/v2/          英文页面
_pages/v2/zh/       中文页面
_data/
  members.yml       团队成员资料（双语，sort_key 控制排序）
  research_directions.yml  研究方向叙述（双语）
  i18n/zh.yml       中文 UI 字符串
_bibliography/
  papers.bib        BibTeX 数据库（150+ 条，含 category/type/clinical 字段）
assets/css/         v2-home.css、v2-pages.css、v2-print.css
assets/js/          v2-nav.js、bibsearch.js
assets/img/
  members/          成员照片
  publication_preview/  论文缩略图（自动生成 480/800/1400 WebP）
  logos/            机构 Logo
scripts/
  fetch_publications.py   PubMed → bib（自动分类）
  classify_paper.py       基于关键词的分类器
  update_citations.py     OpenAlex 引用刷新
  fetch_previews.py       论文缩略图抓取
.github/workflows/  CI：deploy.yml、fetch-publications.yml、update-citations.yml
.codex/skills/      仓库内治理规则（面向贡献者，含 AI 助手）
```

## 内容管理

### 添加团队成员

编辑 [`_data/members.yml`](_data/members.yml)：

```yaml
- name: 姓名
  name_en: English Name
  sort_key: "10"           # 同 role 内的排序权重
  role: basic_researcher   # pi | basic_researcher | clinical_researcher | technician
  title: 研究员
  title_en: Research Fellow
  photo: /assets/img/members/xxx.jpg
  email: xxx@csu.edu.cn
  bio: >                   # 段落间用 <br><br> 分隔
    Line 1.<br><br>
    Line 2.
  bio_zh: >
    第一段。<br><br>
    第二段。
```

### 添加论文

向 [`_bibliography/papers.bib`](_bibliography/papers.bib) 追加 BibTeX 条目。必填字段：`title`、`author`、`journal`、`year`、`doi`。分类字段（`category`、`subcategory`、`publication_type`、`clinical`、`basic`）驱动 `/publications/` 页的筛选 UI。

也可以交给自动化：每周的 PubMed 抓取工作流会自动追加带分类的新论文。

### 编辑研究方向

编辑 [`_data/research_directions.yml`](_data/research_directions.yml) — 每条包含 `intro` / `intro_zh`（首页项目符号列表）与 `narrative` / `narrative_zh`（详情页长文）。

## 自动化

三条定时工作流，无需人工维护数据新鲜度：

| 工作流 | 触发 | 作用 |
| --- | --- | --- |
| `deploy.yml` | push | 构建 Jekyll 站点，缓存 ImageMagick WebP 产物，部署到 gh-pages |
| `fetch-publications.yml` | 每周 | 从 PubMed 查询新论文，自动分类后追加到 papers.bib |
| `update-citations.yml` | 每周 | 从 OpenAlex 刷新 `citation_count` |

## 设计系统

- **配色**：湘雅红 (`#a72126`) + 中南蓝 (`#0852a2`)
- **字体**：衬线标题 (Merriweather) + 衬线正文 (Source Serif 4) + 无衬线 UI (Source Sans 3)
- **中文字体**：Noto Serif SC（标题）+ Noto Sans SC（正文），PI/成员简历采用两端对齐 + 首行缩进
- **设计令牌**：颜色、字体、间距全部通过 `v2-home.css` 的 CSS 变量管理
- **学术排版细节**：旧式数字、自动连字符、孤行/寡行控制

## 治理规则

仓库内的贡献者规则（含 AI 助手）位于 [`AGENTS.md`](AGENTS.md) 与 [`.codex/skills/xy-lilab-site-governance/`](.codex/skills/xy-lilab-site-governance/)。任何结构性改动前请先阅读。

## 许可证

[MIT](LICENSE)
