---
layout: v2-page
permalink: /clinical/
title: Clinical Research
description: Leveraging Xiangya Hospital's clinical resources for skin aging, hair disorder, and inflammatory skin disease research.
show_lead: false
hide_publication_thumbnails: true
---

Leveraging the extensive clinical resources and patient cohorts of the Department of Dermatology at Xiangya Hospital, the lab conducts multicenter clinical studies and translational research across three major directions.

<div class="v2-utility-list">
  <div class="v2-utility-card">
    <h3>Inflammatory skin disease</h3>
    <p>Centered on rosacea and hidradenitis suppurativa, conducting pathogenesis and therapeutic strategy research based on patient-derived samples, and leading multicenter randomized controlled trials of gabapentin, paroxetine, hydroxychloroquine, and other agents.</p>
  </div>
  <div class="v2-utility-card">
    <h3>Hair disorder clinical research</h3>
    <p>Integrating clinical samples from patients with hair loss and hair graying to conduct organ culture, hair follicle regeneration strategies, and clinical trials of novel therapeutics (e.g., multicenter RCTs of JAK inhibitors for alopecia areata).</p>
  </div>
  <div class="v2-utility-card">
    <h3>Skin aging cohorts</h3>
    <p>Longitudinal follow-up cohorts of long-lived populations, integrating multi-omics molecular profiling, aging biomarker screening, and aging-clock model development to explore the molecular basis of healthy aging.</p>
  </div>
</div>

### Clinical collaboration

For collaboration on cohort resources, sample sharing, or translational dermatology studies, contact [{{ site.data.socials.email }}](mailto:{{ site.data.socials.email }}).

<hr>

<div class="v2-section">
  <div class="v2-section__intro">
    <h2>Related publications</h2>
  </div>
  {% include bib_search.liquid %}
  <div class="publications">
    {% bibliography --query @*[clinical=true]* %}
  </div>
</div>
