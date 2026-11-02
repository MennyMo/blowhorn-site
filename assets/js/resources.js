// Resources collection behaviour: category tabs, tag chips, search and
// the video player dialog. Everything is progressive - the page renders
// complete without this script; the script only filters what is already
// there and swaps the poster facade for a playing <video> on request.
// No network calls, no third-party hosts.
(function () {
  "use strict";

  var grid = document.querySelector("[data-collection-grid]");
  var dialog = document.querySelector("[data-video-dialog]");

  // Player dialog: one shared <dialog> for every card on the page.
  if (dialog) {
    var dlgVideo = dialog.querySelector("video");
    var dlgTitle = dialog.querySelector("[data-dialog-title]");
    var openPlayer = function (btn) {
      dlgVideo.innerHTML = "";
      var sources = JSON.parse(btn.getAttribute("data-sources") || "[]");
      sources.forEach(function (s) {
        var el = document.createElement("source");
        el.src = s.src;
        el.type = s.type;
        dlgVideo.appendChild(el);
      });
      var poster = btn.getAttribute("data-poster");
      if (poster) dlgVideo.setAttribute("poster", poster);
      else dlgVideo.removeAttribute("poster");
      dlgTitle.textContent = btn.getAttribute("data-title") || "";
      dlgVideo.load();
      if (typeof dialog.showModal === "function") dialog.showModal();
      dlgVideo.play().catch(function () {});
    };
    document.querySelectorAll("[data-play-video]").forEach(function (btn) {
      btn.addEventListener("click", function () {
        openPlayer(btn);
      });
    });
    dialog.querySelector("[data-dialog-close]").addEventListener("click", function () {
      dialog.close();
    });
    dialog.addEventListener("close", function () {
      dlgVideo.pause();
      dlgVideo.removeAttribute("src");
      dlgVideo.innerHTML = "";
      dlgVideo.load();
    });
  }

  if (!grid) return;

  var cards = Array.prototype.slice.call(grid.querySelectorAll("[data-card]"));
  var tabs = Array.prototype.slice.call(document.querySelectorAll("[data-category-tab]"));
  var chips = Array.prototype.slice.call(document.querySelectorAll("[data-tag-chip]"));
  var search = document.querySelector("[data-collection-search]");
  var status = document.querySelector("[data-collection-status]");
  var activeCategory = "all";
  var activeTags = {};
  var query = "";

  var apply = function () {
    var shown = 0;
    cards.forEach(function (card) {
      var inCategory = activeCategory === "all" || card.getAttribute("data-category") === activeCategory;
      var cardTags = (card.getAttribute("data-tags") || "").split(" ");
      var inTags = Object.keys(activeTags).every(function (t) {
        return cardTags.indexOf(t) !== -1;
      });
      var inQuery = !query || (card.getAttribute("data-search") || "").indexOf(query) !== -1;
      var visible = inCategory && inTags && inQuery;
      card.hidden = !visible;
      if (visible) shown += 1;
    });
    // Hidden cards leave gaps in the deal; hand it out again to the visible ones (card-deal.js).
    window.blowhornCardDeal(grid);
    if (status) {
      status.textContent = shown === cards.length ? "" : shown + " of " + cards.length + " " + (grid.getAttribute("data-collection-noun") || "items") + " shown";
    }
  };

  tabs.forEach(function (tab) {
    tab.addEventListener("click", function () {
      activeCategory = tab.getAttribute("data-category-tab");
      tabs.forEach(function (t) {
        t.setAttribute("aria-selected", t === tab ? "true" : "false");
      });
      apply();
      if (history.replaceState) {
        history.replaceState(null, "", activeCategory === "all" ? location.pathname : "#" + activeCategory);
      }
    });
  });

  chips.forEach(function (chip) {
    chip.addEventListener("click", function () {
      var tag = chip.getAttribute("data-tag-chip");
      if (activeTags[tag]) {
        delete activeTags[tag];
        chip.setAttribute("aria-pressed", "false");
      } else {
        activeTags[tag] = true;
        chip.setAttribute("aria-pressed", "true");
      }
      apply();
    });
  });

  if (search) {
    search.addEventListener("input", function () {
      query = search.value.trim().toLowerCase();
      apply();
    });
  }

  // Deep link: #<category> preselects the tab, like the Layer5 docs
  // videos landing this section is modelled on.
  if (location.hash.length > 1) {
    var wanted = location.hash.slice(1);
    tabs.forEach(function (tab) {
      if (tab.getAttribute("data-category-tab") === wanted) tab.click();
    });
  }

  apply();
})();
