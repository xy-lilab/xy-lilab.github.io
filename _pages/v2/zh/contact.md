---
layout: v2-page
permalink: /zh/contact/
title: 联系我们
lang: zh
page_class: contact
description: 中南大学湘雅医院皮肤科，衰老生物学湖南省重点实验室联系方式。
show_lead: false
---

<div class="v2-contact-grid">
  <div class="v2-contact-info">
    <h3>联系邮箱</h3>
    <p>
      <a href="mailto:liji_xy@csu.edu.cn" style="text-decoration:none;">liji_xy@csu.edu.cn</a>（李吉）<br>
      <a href="mailto:dengzhili@csu.edu.cn" style="text-decoration:none;">dengzhili@csu.edu.cn</a>（邓智利）
    </p>
    <h3>通讯地址</h3>
    <p>
      中南大学湘雅医院皮肤科<br>
      湖南省长沙市开福区湘雅路87号 410008
    </p>
    <p><a href="https://maps.apple.com/?q=中南大学湘雅医院" target="_blank" rel="noopener noreferrer"><i class="fas fa-map-location-dot"></i> 查看地图</a></p>
    {% if site.data.socials.github or site.data.socials.researchgate %}
    <h3>学术主页</h3>
    <ul>
      {% if site.data.socials.github %}<li><strong>GitHub</strong>: <a href="https://github.com/{{ site.data.socials.github }}">github.com/{{ site.data.socials.github }}</a></li>{% endif %}
      {% if site.data.socials.researchgate %}<li><strong>ResearchGate</strong>: <a href="https://www.researchgate.net/profile/{{ site.data.socials.researchgate }}">ResearchGate 主页</a></li>{% endif %}
    </ul>
    {% endif %}
  </div>
  <div class="v2-contact-media">
    <img src="{{ '/assets/img/lab_team.jpg' | relative_url }}" alt="中南大学湘雅医院皮肤科团队合影" loading="lazy">
  </div>
</div>

<hr>

有意加入实验室？请查看 [**加入我们**]({{ '/zh/join/' | relative_url }})，了解在招岗位与申请方式。
