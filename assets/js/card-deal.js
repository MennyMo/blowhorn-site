/* Card variants after a filter (DESIGN.md, "Cards"). A grid that a filter can
   thin out prints its deal as data-card-deal (from
   layouts/_partials/card-deal.html): one variant per card, so that no two
   cards in a row and no card and the one above it match, at every width. The
   deal for k cards is the first k entries of the full one, so after every
   filter the k visible cards take those, in order. Bundled ahead of
   resources.js and action-filter.js, which call it. */
(function () {
  "use strict";

  window.blowhornCardDeal = function (root) {
    var grids = root.matches && root.matches("[data-card-deal]") ? [root] : root.querySelectorAll("[data-card-deal]");
    Array.prototype.forEach.call(grids, function (grid) {
      var deal = (grid.getAttribute("data-card-deal") || "").split(/\s+/).filter(Boolean);
      if (!deal.length) return;
      var names = deal.filter(function (name, i) { return deal.indexOf(name) === i; });
      var selector = names.map(function (name) { return "." + name; }).join(", ");
      var k = 0;
      Array.prototype.forEach.call(grid.querySelectorAll(selector), function (card) {
        var hiddenBy = card.closest("[hidden]");
        if (hiddenBy && grid.contains(hiddenBy)) return;
        names.forEach(function (name) { card.classList.remove(name); });
        card.classList.add(deal[k]);
        k += 1;
      });
    });
  };
})();
