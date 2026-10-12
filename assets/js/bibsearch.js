const initBibSearch = () => {
  const input = document.getElementById("bibsearch");
  if (!input) return;

  const filterCategory = document.getElementById("bibfilter-category");
  const filterSubcategory = document.getElementById("bibfilter-subcategory");
  const filterType = document.getElementById("bibfilter-type");
  const filterNature = document.getElementById("bibfilter-nature");
  const statusEl = document.getElementById("bibfilter-status");

  // Only target the .publications container that is a sibling of the filter UI
  const filterParent = input.closest(".v2-section") || input.closest(".v2-page__content") || input.closest(".v3-publication-surface") || input.closest(".v3-surface") || document.body;
  const groups = Array.from(filterParent.querySelectorAll(".publications ol.bibliography"));
  if (!groups.length) return;

  const cache = groups.map((group) => {
    const heading = group.previousElementSibling?.matches("h2.bibliography")
      ? group.previousElementSibling
      : null;
    const items = Array.from(group.querySelectorAll(":scope > li.bib-entry")).map((item) => ({
      node: item,
      text: item.textContent.toLowerCase(),
      category: (item.dataset.category || "").toLowerCase(),
      subcategory: (item.dataset.subcategory || "").toLowerCase(),
      type: (item.dataset.type || "").toLowerCase(),
      clinical: item.dataset.clinical === "true",
      basic: item.dataset.basic === "true",
    }));
    return { heading, group, items };
  });

  const totalCount = cache.reduce((sum, g) => sum + g.items.length, 0);

  const render = () => {
    const query = input.value.trim().toLowerCase();
    const cat = filterCategory ? filterCategory.value.toLowerCase() : "";
    const subcat = filterSubcategory ? filterSubcategory.value.toLowerCase() : "";
    const type = filterType ? filterType.value.toLowerCase() : "";
    const nature = filterNature ? filterNature.value.toLowerCase() : "";

    let visibleTotal = 0;

    cache.forEach(({ heading, group, items }) => {
      let visibleCount = 0;

      items.forEach(({ node, text, category, subcategory, type: itemType, clinical, basic }) => {
        let visible = true;

        if (query && !text.includes(query)) visible = false;
        if (cat && category !== cat) visible = false;
        if (subcat && subcategory !== subcat) visible = false;
        if (type && itemType !== type) visible = false;
        if (nature === "basic" && !basic) visible = false;
        if (nature === "clinical" && !clinical) visible = false;

        node.hidden = !visible;
        if (visible) visibleCount += 1;
      });

      visibleTotal += visibleCount;
      const hasVisible = visibleCount > 0;
      group.hidden = !hasVisible;
      if (heading) heading.hidden = !hasVisible;
    });

    if (statusEl) {
      const hasFilter = query || cat || subcat || type || nature;
      statusEl.textContent = hasFilter
        ? `${visibleTotal} of ${totalCount} publications`
        : "";
    }
  };

  // Update subcategory options based on category selection
  const updateSubcategoryOptions = () => {
    if (!filterSubcategory || !filterCategory) return;
    const cat = filterCategory.value.toLowerCase();
    const subcatMap = {
      pilosebaceous: ["rosacea", "hair_disorders", "acne"],
      aging: ["skin_aging", "systemic_aging", "wound_healing"],
      other_dermatology: ["psoriasis", "skin_cancer", "atopic_dermatitis", "vitiligo", "other"],
    };

    const options = filterSubcategory.querySelectorAll("option");
    options.forEach((opt) => {
      if (!opt.value) return; // keep "All" option
      if (!cat) {
        opt.hidden = false;
      } else {
        const allowed = subcatMap[cat] || [];
        opt.hidden = !allowed.includes(opt.value);
      }
    });

    // Reset subcategory if current selection is hidden
    const selected = filterSubcategory.querySelector("option:checked");
    if (selected && selected.hidden) {
      filterSubcategory.value = "";
    }
  };

  input.addEventListener("input", render);
  if (filterCategory) {
    filterCategory.addEventListener("change", () => { updateSubcategoryOptions(); render(); });
  }
  if (filterSubcategory) filterSubcategory.addEventListener("change", render);
  if (filterType) filterType.addEventListener("change", render);
  if (filterNature) filterNature.addEventListener("change", render);

  updateSubcategoryOptions();
  render();
};

document.addEventListener("DOMContentLoaded", initBibSearch);
