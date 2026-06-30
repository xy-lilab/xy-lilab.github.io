---
layout: v2-page
permalink: /zh/publications/
title: 论文发表
lang: zh
show_lead: false
hide_publication_thumbnails: true
---
<div class="v2-section">
  <div class="v2-section__intro">
    <h2>代表性论文</h2>
    <p>以下为实验室各研究方向的代表性成果。</p>
  </div>
  <div class="v2-pub-featured">
    {% bibliography --group_by none --query @*[selected=true]* %}
  </div>
</div>

<hr>

<div class="v2-section">
  <div class="v2-section__intro">
    <h2>完整列表</h2>
  </div>
  {% include bib_search.liquid %}
  <div class="publications">
    {% bibliography --query @*[year>=2020] %}
  </div>
</div>
