---
layout: v2-page
permalink: /publications/
title: Our Publications
description: Selected and complete publications from the Li Lab.
show_lead: false
hide_publication_thumbnails: true
---
<div class="v2-section">
  <div class="v2-section__intro">
    <h2>Selected papers</h2>
    <p>Key publications that define the lab's current research directions.</p>
  </div>
  <div class="v2-pub-featured">
    {% bibliography --group_by none --query @*[selected=true]* %}
  </div>
</div>

<hr>

<div class="v2-section">
  <div class="v2-section__intro">
    <h2>Complete list</h2>
  </div>
  {% include bib_search.liquid %}
  <div class="publications">
    {% bibliography %}
  </div>
</div>
