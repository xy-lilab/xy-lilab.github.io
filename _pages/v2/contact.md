---
layout: v2-page
permalink: /contact/
title: Contact Us
page_class: contact
show_lead: false
---

<div class="v2-contact-grid">
  <div class="v2-contact-info">
    <h3>Email</h3>
    <p>
      <a href="mailto:liji_xy@csu.edu.cn" style="text-decoration:none;">liji_xy@csu.edu.cn</a> (Ji Li)<br>
      <a href="mailto:dengzhili@csu.edu.cn" style="text-decoration:none;">dengzhili@csu.edu.cn</a> (Zhili Deng)
    </p>
    <h3>Address</h3>
    <p>
      Department of Dermatology<br>
      Xiangya Hospital, Central South University<br>
      87 Xiangya Road, Kaifu District<br>
      Changsha, Hunan, China 410008
    </p>
    <p><a href="https://maps.apple.com/?q=中南大学湘雅医院" target="_blank" rel="noopener noreferrer"><i class="fas fa-map-location-dot"></i> View on Map</a></p>
    {% if site.data.socials.github or site.data.socials.researchgate %}
    <h3>Online</h3>
    <ul>
      {% if site.data.socials.github %}<li><strong>GitHub</strong>: <a href="https://github.com/{{ site.data.socials.github }}">github.com/{{ site.data.socials.github }}</a></li>{% endif %}
      {% if site.data.socials.researchgate %}<li><strong>ResearchGate</strong>: <a href="https://www.researchgate.net/profile/{{ site.data.socials.researchgate }}">ResearchGate profile</a></li>{% endif %}
    </ul>
    {% endif %}
  </div>
  <div class="v2-contact-media">
    <img src="{{ '/assets/img/lab_team.jpg' | relative_url }}" alt="The dermatology team at Xiangya Hospital, Central South University" loading="lazy">
  </div>
</div>

<hr>

Interested in joining the lab? See [**Join Us**]({{ '/join/' | relative_url }}) for current openings and how to apply.
