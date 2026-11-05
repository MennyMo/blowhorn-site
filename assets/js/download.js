// Fills the Download section from the newest desktop release on
// blowhorn-ai/blowhorn-site. This repository also publishes blowhorn-axi
// releases (tags axi-vX.Y.Z), and GitHub's "latest" release is whichever
// stable release was created most recently, so /releases/latest points at
// an axi release whenever one is newer, and its download URL 404s. The
// desktop release is therefore picked by rule, the same rule the app's
// update check uses: the newest non-draft, non-prerelease release whose
// tag is exactly vX.Y.Z and which carries the fixed-name alias
// (Blowhorn-mac.dmg). The newest 100 releases are read (not
// /releases/latest), so "no desktop release yet" is an empty result rather
// than a wrong one.
//
// States, in order of preference:
//   1. A desktop release carries the alias: the page's button (to
//      /download/thanks/) stays; version, size, date, release notes and
//      checksums are filled in.
//   2. No desktop release yet: the static card stays.
//   3. Any failure (rate limit, outage, offline): the static card stays,
//      and its button still downloads the build pinned in
//      data/download.json.
(function () {
  "use strict";

  var card = document.getElementById("download-status");
  if (!card || !window.fetch) {
    return;
  }
  var repo = card.getAttribute("data-repo");
  var alias = card.getAttribute("data-asset");
  var releasesUrl = "https://github.com/" + repo + "/releases";

  function el(tag, text, attrs) {
    var node = document.createElement(tag);
    if (text) {
      node.textContent = text;
    }
    Object.keys(attrs || {}).forEach(function (key) {
      node.setAttribute(key, attrs[key]);
    });
    return node;
  }

  function megabytes(bytes) {
    return Math.max(1, Math.round(bytes / 1048576)) + " MB";
  }

  function publishedOn(iso) {
    var date = new Date(iso);
    if (isNaN(date.getTime())) {
      return null;
    }
    return date.toLocaleDateString(undefined, { year: "numeric", month: "long", day: "numeric" });
  }

  function replaceCard(children) {
    card.textContent = "";
    children.forEach(function (child) {
      card.appendChild(child);
    });
  }

  function showRelease(release) {
    var assets = Array.isArray(release.assets) ? release.assets : [];
    var version = release.tag_name || release.name || "";
    var aliasAsset = assets.find(function (a) { return a.name === alias; });
    // The file a visitor saves is named after the URL, so the page shows the
    // versioned disk image (same bytes as the alias) and falls back to the alias.
    var versioned = assets.find(function (a) {
      return a.name === "Blowhorn-" + version.replace(/^v/, "") + "-mac-universal.dmg";
    }) || aliasAsset;
    var sums = assets.find(function (a) { return a.name === "SHA256SUMS.txt"; });
    if (!aliasAsset) {
      return;
    }

    // Keep the page's own button (it goes to the thanks page, which starts the
    // download); only the label, file size and details below it change.
    var icon = card.querySelector(".download-icon");
    var requirement = card.querySelector(".download-req");
    var actions = card.querySelector(".actions");
    var fallback = card.querySelector(".download-fallback");
    var size = actions && actions.querySelector(".caption");
    if (size) {
      size.textContent = versioned.name + " · " + megabytes(versioned.size);
    }
    var title = el("h2", "Blowhorn " + version + " for Mac", { class: "h3" });
    var body = el("p", "The Mac app runs your activities and installs the Blowhorn command.");
    var children = (icon ? [icon] : []).concat([title, body], requirement ? [requirement] : [], [actions], fallback ? [fallback] : []);

    var meta = el("p", null, { class: "meta caption" });
    var date = release.published_at ? publishedOn(release.published_at) : null;
    if (date) {
      meta.appendChild(el("span", "Published " + date));
    }
    var notes = el("span");
    notes.appendChild(el("a", "Release notes", { href: release.html_url || releasesUrl }));
    meta.appendChild(notes);
    if (sums) {
      var checksum = el("span");
      checksum.appendChild(el("a", "SHA256SUMS.txt", { href: sums.browser_download_url }));
      meta.appendChild(checksum);
    }
    children.push(meta);
    replaceCard(children);
  }

  var api = "https://api.github.com/repos/" + repo + "/releases";
  var headers = { Accept: "application/vnd.github+json" };

  fetch(api + "?per_page=100", { headers: headers })
    .then(function (res) {
      if (!res.ok) {
        throw new Error("GitHub answered " + res.status);
      }
      return res.json();
    })
    .then(function (releases) {
      if (!Array.isArray(releases)) {
        throw new Error("GitHub answered with something other than a release list");
      }
      return releases.find(function (r) {
        if (!r || r.draft || r.prerelease) {
          return false;
        }
        if (!/^v\d+\.\d+\.\d+$/.test(r.tag_name || "")) {
          return false;
        }
        var assets = Array.isArray(r.assets) ? r.assets : [];
        return assets.some(function (a) { return a.name === alias; });
      }) || null;
    })
    .then(function (stable) {
      if (stable) {
        showRelease(stable);
      }
    })
    .catch(function () {
      // The static card already downloads the pinned build, so a failed
      // lookup only means no version details. Never claim "no build" on an error.
    });
})();

// Windows notify signup on the coming-soon card: the button reveals the
// waitlist form (topic "windows", stored separately from the newsletter
// list), and submitting it posts JSON to the signup service and shows an
// inline result, mirroring assets/js/signup.js. Without JavaScript, or
// without fetch, the toggle stays hidden and the form stays visible: it
// posts to the service, which redirects to a thanks page. An invalid
// address is caught by the browser's own validation, and a failed
// submission leaves the entered address in place.
(function () {
  "use strict";

  var toggle = document.getElementById("windows-notify-toggle");
  var form = document.getElementById("windows-notify-form");
  if (!toggle || !form || !window.fetch) {
    return;
  }
  var status = document.getElementById("windows-notify-status");
  var email = document.getElementById("windows-notify-email");
  toggle.hidden = false;
  form.hidden = true;
  toggle.addEventListener("click", function () {
    var open = form.hidden;
    form.hidden = !open;
    toggle.setAttribute("aria-expanded", open ? "true" : "false");
    if (open && email) {
      email.focus();
    }
  });
  form.addEventListener("submit", function (ev) {
    ev.preventDefault();
    var data = {};
    new FormData(form).forEach(function (value, key) {
      data[key] = value;
    });
    fetch(form.action, {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify(data),
    })
      .then(function (res) {
        return res.json().then(function (body) {
          return { res: res, body: body };
        });
      })
      .then(function (pair) {
        if (pair.res.ok && pair.body.ok) {
          form.reset();
          status.textContent = "You are on the list. We will email you when Blowhorn for Windows is ready.";
        } else {
          status.textContent = (pair.body && pair.body.error) || "Something went wrong. Please try again.";
        }
      })
      .catch(function () {
        status.textContent = "Something went wrong. Please try again.";
      });
  });
})();
