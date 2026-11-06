/* API reference (layouts/_partials/rest-apis/viewer.html). The page is complete
   without this script: every operation is a native <details>. This adds a
   filter, expand/collapse all, and opening the operation a #fragment names
   (a browser does not open a closed <details> for a link to it). No
   dependencies, no network. */
(function () {
  "use strict";

  var root = document.querySelector("[data-api-ref]");
  if (!root) { return; }

  var controls = root.querySelector("[data-api-controls]");
  var input = root.querySelector("[data-api-filter]");
  var toggle = root.querySelector("[data-api-toggle]");
  var status = root.querySelector("[data-api-status]");
  var empty = root.querySelector("[data-api-empty]");
  var ops = Array.prototype.slice.call(root.querySelectorAll("[data-api-op]"));
  var groups = Array.prototype.slice.call(root.querySelectorAll("[data-api-group]"));
  var links = Array.prototype.slice.call(root.querySelectorAll("[data-api-resource-link]"));

  function visibleOps() {
    return ops.filter(function (op) { return !op.hidden; });
  }

  function syncToggle() {
    var visible = visibleOps();
    var allOpen = visible.length > 0 && visible.every(function (op) { return op.open; });
    toggle.textContent = allOpen ? "Collapse all" : "Expand all";
    toggle.setAttribute("aria-pressed", allOpen ? "true" : "false");
    toggle.disabled = visible.length === 0;
  }

  function applyFilter() {
    var terms = input.value.toLowerCase().split(/\s+/).filter(Boolean);
    var shown = 0;
    ops.forEach(function (op) {
      var haystack = op.getAttribute("data-search") || "";
      var match = terms.every(function (term) { return haystack.indexOf(term) !== -1; });
      op.hidden = !match;
      if (match) { shown += 1; }
    });
    groups.forEach(function (group) {
      var any = group.querySelector("[data-api-op]:not([hidden])") !== null;
      group.hidden = !any;
      links.forEach(function (link) {
        if (link.getAttribute("data-api-resource-link") === group.id) { link.hidden = !any; }
      });
    });
    empty.hidden = shown > 0;
    status.textContent = terms.length
      ? shown + " of " + ops.length + " operations match."
      : "";
    syncToggle();
  }

  function openFromHash() {
    var id;
    try {
      id = decodeURIComponent(window.location.hash.slice(1));
    } catch (err) {
      // A malformed percent escape ("#%", "#%E0%A4%A") names no operation.
      if (err instanceof URIError) { return; }
      throw err;
    }
    if (!id) { return; }
    var target = document.getElementById(id);
    if (!target || !root.contains(target)) { return; }
    var op = target.closest("[data-api-op]");
    if (!op) { return; }
    if (op.hidden) { input.value = ""; applyFilter(); }
    op.open = true;
    op.scrollIntoView();
  }

  input.addEventListener("input", applyFilter);
  toggle.addEventListener("click", function () {
    var visible = visibleOps();
    var open = !visible.every(function (op) { return op.open; });
    visible.forEach(function (op) { op.open = open; });
    syncToggle();
  });
  // The toggle event does not bubble; catch it on the way down.
  root.addEventListener("toggle", syncToggle, true);
  window.addEventListener("hashchange", openFromHash);

  controls.hidden = false;
  syncToggle();
  openFromHash();
})();
