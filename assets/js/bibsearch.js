const enhanceBibFilters = (selects) => {
  let openFilter = null;

  const filters = selects.filter(Boolean).map((select) => {
    const wrapper = document.createElement("div");
    wrapper.className = "bib-filter";
    const trigger = document.createElement("button");
    trigger.type = "button";
    trigger.className = "bib-filter__trigger";
    trigger.setAttribute("role", "combobox");
    trigger.setAttribute("aria-haspopup", "listbox");
    trigger.setAttribute("aria-expanded", "false");
    trigger.setAttribute("aria-label", select.getAttribute("aria-label") || select.options[0]?.label || "");
    const value = document.createElement("span");
    value.className = "bib-filter__value";
    trigger.append(value);

    const menu = document.createElement("div");
    menu.id = `${select.id}-options`;
    menu.className = "bib-filter__options";
    menu.setAttribute("role", "listbox");
    menu.setAttribute("aria-label", trigger.getAttribute("aria-label"));
    menu.hidden = true;
    trigger.setAttribute("aria-controls", menu.id);

    let options = [];
    let activeIndex = -1;
    let typed = "";
    let typedAt = 0;

    const activate = (index, scroll = true) => {
      activeIndex = Math.max(0, Math.min(index, options.length - 1));
      Array.from(menu.children).forEach((node, i) => {
        node.classList.toggle("is-active", i === activeIndex);
        node.setAttribute("aria-selected", String(i === activeIndex));
      });
      const active = menu.children[activeIndex];
      if (active) {
        trigger.setAttribute("aria-activedescendant", active.id);
        if (scroll) active.scrollIntoView({ block: "nearest" });
      }
    };

    const sync = () => {
      value.textContent = select.selectedOptions[0]?.label || "";
      trigger.disabled = select.disabled;
      options = Array.from(select.options).filter((option) => !option.hidden && !option.disabled);
      menu.replaceChildren(...options.map((option, index) => {
        const node = document.createElement("div");
        node.id = `${select.id}-option-${option.index}`;
        node.className = "bib-filter__option";
        node.dataset.index = index;
        node.setAttribute("role", "option");
        node.setAttribute("aria-selected", String(option.selected));
        node.textContent = option.label;
        return node;
      }));
      activeIndex = options.findIndex((option) => option.selected);
      if (!menu.hidden) activate(activeIndex, false);
    };

    const close = () => {
      menu.hidden = true;
      trigger.setAttribute("aria-expanded", "false");
      trigger.removeAttribute("aria-activedescendant");
      typed = "";
      if (openFilter === filter) openFilter = null;
    };

    const open = () => {
      if (openFilter !== filter) openFilter?.close();
      sync();
      if (trigger.disabled || !options.length) return;
      menu.hidden = false;
      trigger.setAttribute("aria-expanded", "true");
      openFilter = filter;
      activate(activeIndex);
    };

    const choose = (index) => {
      const option = options[index];
      if (!option || option.hidden || option.disabled) return;
      close();
      if (select.value !== option.value) {
        select.value = option.value;
        select.dispatchEvent(new Event("change", { bubbles: true }));
      }
      sync();
    };

    const filter = { wrapper, sync, close };
    trigger.addEventListener("click", () => {
      if (menu.hidden) open();
      else close();
      trigger.focus({ preventScroll: true });
    });
    trigger.addEventListener("keydown", (event) => {
      if (event.isComposing || event.ctrlKey || event.metaKey || event.altKey) return;
      const { key } = event;
      if (key === "Escape") {
        if (!menu.hidden) { event.preventDefault(); close(); }
        return;
      }
      if (key === "Tab") {
        if (!menu.hidden) choose(activeIndex);
        return;
      }
      if (key === "Enter" || key === " ") {
        event.preventDefault();
        if (menu.hidden) open();
        else choose(activeIndex);
        return;
      }
      if (["ArrowDown", "ArrowUp", "Home", "End"].includes(key)) {
        event.preventDefault();
        const wasClosed = menu.hidden;
        if (wasClosed) open();
        if (key === "Home") activate(0);
        else if (key === "End") activate(options.length - 1);
        else if (!wasClosed) activate(activeIndex + (key === "ArrowDown" ? 1 : -1));
        return;
      }
      if (key.length === 1) {
        event.preventDefault();
        if (menu.hidden) open();
        const now = Date.now();
        typed = now - typedAt > 700 ? key : typed + key;
        typedAt = now;
        const chars = typed.toLocaleLowerCase();
        const search = Array.from(chars).every((char) => char === chars[0]) ? chars[0] : chars;
        const start = search.length === 1 ? activeIndex + 1 : activeIndex;
        for (let offset = 0; offset < options.length; offset += 1) {
          const index = (start + offset + options.length) % options.length;
          if (options[index].label.toLocaleLowerCase().startsWith(search)) {
            activate(index);
            break;
          }
        }
      }
    });

    // Keep focus on the combobox without blocking touch scrolling in its menu.
    menu.addEventListener("mousedown", (event) => event.preventDefault());
    menu.addEventListener("click", (event) => {
      const option = event.target.closest(".bib-filter__option");
      if (!option) return;
      choose(Number(option.dataset.index));
      trigger.focus({ preventScroll: true });
    });
    wrapper.addEventListener("focusout", (event) => {
      if (!wrapper.contains(event.relatedTarget)) close();
    });

    sync();
    select.before(wrapper);
    wrapper.append(select, trigger, menu);
    select.hidden = true;
    return filter;
  });

  document.addEventListener("pointerdown", (event) => {
    if (openFilter && !openFilter.wrapper.contains(event.target)) openFilter.close();
  });
  return filters;
};

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
  const filters = enhanceBibFilters([filterCategory, filterSubcategory, filterType, filterNature]);

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
    // Direction changes can silently reset the native subtype value/options.
    filters.forEach((filter) => filter.sync());
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
