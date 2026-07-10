---
layout: v2-page
permalink: /zh/clinical/
title: 临床研究
lang: zh
description: 依托湘雅医院丰富临床资源，开展皮肤衰老、毛发疾病及炎症性皮肤病的临床与转化研究。
show_lead: false
hide_publication_thumbnails: true
---

依托湘雅医院皮肤科的丰富临床资源和患者队列，实验室围绕三大方向开展多中心临床研究与转化医学研究。

<div class="v2-utility-list">
  <div class="v2-utility-card">
    <h3>炎症性皮肤病</h3>
    <p>以玫瑰痤疮与化脓性汗腺炎为核心，基于患者来源样本开展发病机制与治疗策略研究，牵头开展加巴喷丁、帕罗西汀、羟氯喹等多中心随机对照试验。</p>
  </div>
  <div class="v2-utility-card">
    <h3>毛发疾病临床研究</h3>
    <p>整合脱发与白发患者的临床样本，开展器官培养、毛囊再生策略及新药临床试验（如 JAK 抑制剂治疗斑秃的多中心 RCT）。</p>
  </div>
  <div class="v2-utility-card">
    <h3>皮肤衰老队列</h3>
    <p>建立长寿人群纵向随访队列，结合多组学分子谱分析、衰老生物标志物筛选及衰老时钟模型开发，探索健康衰老的分子基础。</p>
  </div>
</div>

### 临床合作

欢迎在队列资源、样本共享或转化皮肤病学研究方面开展合作，请联系 [{{ site.data.socials.email }}](mailto:{{ site.data.socials.email }})。

<hr>

<div class="v2-section">
  <div class="v2-section__intro">
    <h2>相关论文</h2>
  </div>
  {% include bib_search.liquid %}
  <div class="publications">
    {% bibliography --query @*[clinical=true]* %}
  </div>
</div>
