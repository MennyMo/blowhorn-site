/* Signal homepage: interactive hero demo and platforms treatments.
   Respects prefers-reduced-motion. No third-party hosts. */
(function () {
  var reduce = false;
  try {
    reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  } catch (e) {}

  function stepsFromPage() {
    var el = document.getElementById("hero-demo-data");
    var fallback = ["Queued", "Posting as you", "Went out"];
    if (!el) return fallback;
    try {
      var data = JSON.parse(el.textContent);
      if (data && data.steps && data.steps.length === 3) return data.steps;
    } catch (err) {}
    return fallback;
  }

  function setPill(pill, state, text) {
    if (!pill) return;
    pill.classList.remove("is-queued", "is-pending");
    if (state) pill.classList.add(state);
    var t = pill.querySelector(".pill-text");
    if (t) t.textContent = text;
  }

  function runDelivery(root, steps) {
    var cards = root.querySelectorAll("[data-demo-card]:not([hidden])");
    var summary = root.querySelector("[data-demo-summary]");
    var i;
    if (!cards.length) {
      setPill(summary, null, "Pick a network");
      return;
    }
    if (reduce) {
      for (i = 0; i < cards.length; i++) {
        setPill(cards[i].querySelector("[data-status]"), null, steps[2]);
      }
      setPill(summary, null, steps[2]);
      return;
    }
    for (i = 0; i < cards.length; i++) {
      setPill(cards[i].querySelector("[data-status]"), "is-queued", steps[0]);
    }
    setPill(summary, "is-pending", steps[1]);
    Array.prototype.forEach.call(cards, function (card, idx) {
      var pill = card.querySelector("[data-status]");
      window.setTimeout(function () {
        setPill(pill, "is-pending", steps[1]);
      }, 400 + idx * 520);
      window.setTimeout(function () {
        setPill(pill, null, steps[2]);
        if (idx === cards.length - 1) setPill(summary, null, steps[2]);
      }, 1000 + idx * 520);
    });
  }

  function bindDemo(root) {
    var form = root.querySelector("[data-demo-form]");
    var input = root.querySelector("[data-demo-input]");
    var msg = root.querySelector("[data-demo-msg]");
    var send = root.querySelector("[data-demo-send]");
    var summary = root.querySelector("[data-demo-summary]");
    var steps = stepsFromPage();
    var app = root.querySelector("[data-component=\"app-mock\"]");

    function selectedCount() {
      var n = 0;
      root.querySelectorAll("[data-demo-net]").forEach(function (box) {
        if (box.checked) n += 1;
      });
      return n;
    }

    function syncNets() {
      var any = false;
      root.querySelectorAll("[data-demo-net]").forEach(function (box) {
        var card = root.querySelector('[data-demo-card="' + box.value + '"]');
        if (card) card.hidden = !box.checked;
        if (box.checked) any = true;
      });
      if (send) send.disabled = !any;
      if (!any) setPill(summary, null, "Pick a network");
      return any;
    }

    if (input && msg) {
      input.addEventListener("input", function () {
        msg.textContent = input.value.trim() || "Type your announcement above.";
      });
      input.addEventListener("keydown", function (ev) {
        if ((ev.metaKey || ev.ctrlKey) && ev.key === "Enter") {
          ev.preventDefault();
          if (form && selectedCount()) form.requestSubmit();
        }
      });
    }
    root.querySelectorAll("[data-demo-net]").forEach(function (box) {
      box.addEventListener("change", syncNets);
    });
    if (form) {
      form.addEventListener("submit", function (ev) {
        ev.preventDefault();
        if (!syncNets()) return;
        runDelivery(root, steps);
      });
    }
    syncNets();
    if (app && !reduce) {
      var started = false;
      var io = new IntersectionObserver(function (entries, obs) {
        entries.forEach(function (entry) {
          if (!entry.isIntersecting || started) return;
          if (!selectedCount()) return;
          started = true;
          obs.disconnect();
          runDelivery(root, steps);
        });
      }, { threshold: 0.2 });
      io.observe(app);
    }
  }

  document.querySelectorAll("[data-hero-demo]").forEach(bindDemo);

  function defaultPlatTab(section, tabs) {
    var on = section.querySelector("[data-plat-tab].is-on");
    if (on) return on.getAttribute("data-plat-tab");
    return tabs.length ? tabs[0].getAttribute("data-plat-tab") : "";
  }

  function selectTab(section, id) {
    section.querySelectorAll("[data-plat-tab]").forEach(function (tab) {
      var on = tab.getAttribute("data-plat-tab") === id;
      tab.classList.toggle("is-on", on);
      tab.setAttribute("aria-selected", on ? "true" : "false");
      tab.tabIndex = on ? 0 : -1;
    });
    section.querySelectorAll("[data-plat-panel]").forEach(function (panel) {
      var on = panel.getAttribute("data-plat-panel") === id;
      panel.classList.toggle("is-on", on);
      panel.hidden = !on;
    });
  }

  function bindPlatforms(section) {
    section.classList.add("is-plat-enhanced");
    var tabs = Array.prototype.slice.call(section.querySelectorAll("[data-plat-tab]"));
    tabs.forEach(function (tab, index) {
      tab.tabIndex = tab.classList.contains("is-on") ? 0 : -1;
      tab.addEventListener("click", function (ev) {
        ev.preventDefault();
        selectTab(section, tab.getAttribute("data-plat-tab"));
      });
      tab.addEventListener("keydown", function (ev) {
        var next = index;
        if (ev.key === "ArrowRight" || ev.key === "ArrowDown") next = (index + 1) % tabs.length;
        else if (ev.key === "ArrowLeft" || ev.key === "ArrowUp") next = (index - 1 + tabs.length) % tabs.length;
        else if (ev.key === "Home") next = 0;
        else if (ev.key === "End") next = tabs.length - 1;
        else return;
        ev.preventDefault();
        tabs[next].focus();
        selectTab(section, tabs[next].getAttribute("data-plat-tab"));
      });
    });

    var roleBtns = Array.prototype.slice.call(section.querySelectorAll("[data-plat-role]"));
    function applyRole(id) {
      roleBtns.forEach(function (btn) {
        var on = btn.getAttribute("data-plat-role") === id;
        btn.classList.toggle("is-on", on);
        btn.setAttribute("aria-pressed", on ? "true" : "false");
      });
      section.querySelectorAll("[data-plat-roles]").forEach(function (item) {
        var roles = (item.getAttribute("data-plat-roles") || "").split(/\s+/);
        var hit = roles.indexOf(id) !== -1;
        item.classList.toggle("is-hot", hit);
        item.classList.toggle("is-dim", !hit);
      });
    }
    if (roleBtns.length) applyRole(roleBtns[0].getAttribute("data-plat-role"));
    roleBtns.forEach(function (btn) {
      btn.addEventListener("click", function () {
        applyRole(btn.getAttribute("data-plat-role"));
      });
    });

    section.querySelectorAll("[data-constellation-total]").forEach(function (orbit) {
      var total = parseInt(orbit.getAttribute("data-constellation-total"), 10) || 11;
      orbit.style.setProperty("--total", String(total));
      Array.prototype.forEach.call(orbit.children, function (item, i) {
        var n = item.getAttribute("data-n");
        item.style.setProperty("--n", n || String(i));
      });
    });

    var hash = (window.location.hash || "").replace(/^#/, "");
    var initial = defaultPlatTab(section, tabs);
    if (hash.indexOf("plat-panel-") === 0) {
      initial = hash.slice("plat-panel-".length);
    } else if (hash.indexOf("action-") === 0) {
      initial = "action";
    }
    if (!initial || !section.querySelector('[data-plat-panel="' + initial + '"]')) {
      initial = defaultPlatTab(section, tabs);
    }
    selectTab(section, initial);

    section.querySelectorAll("[data-constellation]").forEach(function (wrap) {
      var btn = wrap.querySelector("[data-constellation-pause]");
      if (!btn) return;
      btn.addEventListener("click", function () {
        var paused = wrap.classList.toggle("is-paused");
        btn.setAttribute("aria-pressed", paused ? "true" : "false");
        btn.textContent = paused ? "Play motion" : "Pause motion";
      });
    });
  }

  document.querySelectorAll("[data-platforms]").forEach(bindPlatforms);
})();
