/* By-action filter for /integrations/ and the home platforms treatment.
   Without this file the chips are in-page links to #action-<id> sections.
   With it, chips filter the catalog cards and hide the stacked duplicates. */
(function () {
  function apply(root, id) {
    var chips = Array.prototype.slice.call(root.querySelectorAll("[data-action-chip]"));
    chips.forEach(function (chip) {
      var on = (chip.getAttribute("data-action-chip") || "") === id;
      chip.classList.toggle("is-on", on);
      if (chip.hasAttribute("data-action-chip")) {
        chip.setAttribute("aria-current", on ? "true" : "false");
      }
    });
    root.querySelectorAll("[data-action-card]").forEach(function (card) {
      var actions = (card.getAttribute("data-actions") || "").split(/\s+/);
      var hit = !id || actions.indexOf(id) !== -1;
      card.hidden = !hit;
      var wrap = card.closest("li");
      if (wrap && wrap !== card) wrap.hidden = !hit;
    });
    // Hidden cards leave gaps in the deal; hand it out again to the visible ones (card-deal.js).
    window.blowhornCardDeal(root);
    root.querySelectorAll("[data-action-catalog]").forEach(function (section) {
      var visible = section.querySelectorAll("[data-action-card]:not([hidden])");
      section.hidden = id !== "" && visible.length === 0;
    });
    var catalog = root.querySelector("[data-action-card]");
    root.querySelectorAll("[data-action-group]").forEach(function (group) {
      if (catalog) {
        group.hidden = true;
        return;
      }
      group.hidden = id !== "" && group.getAttribute("data-action-group") !== id;
    });
  }

  function bind(root) {
    var chips = Array.prototype.slice.call(root.querySelectorAll("[data-action-chip]"));
    if (!chips.length) return;
    root.classList.add("is-action-enhanced");
    chips.forEach(function (chip) {
      chip.addEventListener("click", function (ev) {
        var id = chip.getAttribute("data-action-chip") || "";
        ev.preventDefault();
        apply(root, id);
        if (id) {
          try {
            history.replaceState(null, "", "#" + "action-" + id);
          } catch (err) {}
        } else {
          try {
            history.replaceState(null, "", window.location.pathname + window.location.search);
          } catch (err) {}
        }
      });
    });
    var hash = (window.location.hash || "").replace(/^#/, "");
    var start = "";
    if (hash.indexOf("action-") === 0) start = hash.slice("action-".length);
    apply(root, start);
    window.addEventListener("hashchange", function () {
      var next = (window.location.hash || "").replace(/^#/, "");
      if (next.indexOf("action-") === 0) apply(root, next.slice("action-".length));
      else if (!next) apply(root, "");
    });
  }

  document.querySelectorAll("[data-action-filter]").forEach(bind);
})();
