// Consent-gated attribution events for the MCP connection guides
// (layouts/_partials/docs-attribution.html, data/docs_events.json,
// docs/docs-attribution.md). Sends docs_guide_view, docs_snippet_copy and
// docs_outbound_click through the gtag() the head already defines, so no new
// host loads. Nothing is stored, listened for or sent until localStorage
// blowhorn-consent is "granted"; consent given later on the page starts it
// from that point (consent.js dispatches the config's consent_event).
// Every other analytics page loads it too, for the first-touch capture only:
// it stores the session's attribution and sends nothing.
// The builders below are pure and exported for
// .github/scripts/test_docs_attribution.py; the DOM wiring is at the end.
(function () {
  'use strict';

  var MAX = 100; // GA4's limit on a parameter value
  var NONE = '(none)';

  function clip(value) {
    return String(value == null ? '' : value).slice(0, MAX);
  }

  function isTracked(path, pages) {
    return (pages || []).some(function (prefix) { return path.indexOf(prefix) === 0; });
  }

  // The page slug: /docs/reference/mcp-server/ -> mcp-server.
  function guideOf(path) {
    var parts = String(path).split('/').filter(Boolean);
    var last = (parts[parts.length - 1] || 'home').replace(/\.html$/, '').toLowerCase();
    return clip(last.replace(/[^a-z0-9-]/g, '-').replace(/^-+/, '') || 'home');
  }

  // A heading id or a duplicate's id (claude-code-1) to the client name;
  // '' when it names no client.
  function clientName(key, clients) {
    if (!key) return '';
    key = String(key);
    if (Object.prototype.hasOwnProperty.call(clients, key)) return clients[key];
    var base = key.replace(/-\d+$/, '');
    return Object.prototype.hasOwnProperty.call(clients, base) ? clients[base] : '';
  }

  // headings: every h2/h3 before the element, in document order, as
  // {level, id}. Walks up the enclosing sections only: a sibling heading
  // that is not a client ends a client's section.
  function clientFor(headings, config, pageClient) {
    var limit = Infinity;
    for (var i = headings.length - 1; i >= 0; i--) {
      var h = headings[i];
      if (h.level >= limit) continue;
      var name = clientName(h.id, config.clients);
      if (name) return name;
      limit = h.level;
      if (limit <= 2) break;
    }
    return clientName(pageClient, config.clients) || config.default_client;
  }

  function hashClient(hash, config, pageClient) {
    var id = String(hash || '').replace(/^#/, '');
    try { id = decodeURIComponent(id); } catch (e) { /* keep it raw */ }
    return clientName(id, config.clients) || clientName(pageClient, config.clients) || config.default_client;
  }

  function snippetKind(lang, config) {
    var kinds = config.snippet_kinds;
    lang = String(lang || '').toLowerCase();
    return Object.prototype.hasOwnProperty.call(kinds, lang) ? kinds[lang] : 'other';
  }

  // Scheme, host and path only: no query string, no fragment, no userinfo.
  function cleanUrl(url) {
    return clip(url.protocol + '//' + url.host + url.pathname);
  }

  // url: a parsed URL. The first rule that matches names the kind; null when
  // the link is none of them.
  function linkKind(url, config) {
    if (!url || (url.protocol !== 'https:' && url.protocol !== 'http:')) return null;
    var host = url.hostname.toLowerCase();
    var rules = config.outbound;
    for (var i = 0; i < rules.length; i++) {
      var rule = rules[i];
      if (rule.hosts.indexOf(host) === -1) continue;
      if (!rule.paths || rule.paths.some(function (p) { return new RegExp(p).test(url.pathname); })) return rule.kind;
    }
    return null;
  }

  // The referrer's host, or (none) when there is none or it is this site.
  function referrerHost(referrer, pageHost, config) {
    if (!referrer) return NONE;
    var host;
    try { host = new URL(referrer).host.toLowerCase(); } catch (e) { return NONE; }
    if (!host || host === pageHost || config.internal_hosts.indexOf(host) !== -1) return NONE;
    return clip(host);
  }

  // First-touch attribution from the landing page: its utm_* parameters, the
  // external referrer's host and its path. landing_guide is (none) off the
  // tracked guides; firstTouch fills it from the first guide seen.
  function captureAttribution(search, referrer, pageHost, path, config, tracked) {
    var params = new URLSearchParams(search || '');
    var out = {};
    config.attribution_params.slice(0, config.utm_params.length).forEach(function (name, i) {
      var v = (params.get(config.utm_params[i]) || '').trim();
      out[name] = v ? clip(v) : NONE;
    });
    out.first_referrer_host = referrerHost(referrer, pageHost, config);
    out.landing_guide = tracked ? guideOf(path) : NONE;
    out.landing_page = clip(path);
    return out;
  }

  // The session's first touch wins; only a missing landing_guide is filled.
  function firstTouch(stored, fresh) {
    if (!stored || typeof stored !== 'object') return fresh;
    if ((!stored.landing_guide || stored.landing_guide === NONE) && fresh.landing_guide !== NONE) {
      stored.landing_guide = fresh.landing_guide;
    }
    return stored;
  }

  function withAttribution(params, attribution, config) {
    config.attribution_params.forEach(function (name) {
      params[name] = attribution && attribution[name] ? clip(attribution[name]) : NONE;
    });
    return params;
  }

  function guideView(ctx, config) {
    return {
      name: 'docs_guide_view',
      params: withAttribution({
        page_path: clip(ctx.path),
        guide: guideOf(ctx.path),
        client: hashClient(ctx.hash, config, ctx.pageClient)
      }, ctx.attribution, config)
    };
  }

  // card: {lang, title, headings}
  function snippetCopy(ctx, card, config) {
    return {
      name: 'docs_snippet_copy',
      params: withAttribution({
        page_path: clip(ctx.path),
        client: clientFor(card.headings, config, ctx.pageClient),
        snippet_kind: snippetKind(card.lang, config),
        snippet_title: clip(String(card.title || '').trim())
      }, ctx.attribution, config)
    };
  }

  // link: {url (parsed), headings}; null when the link is not tracked.
  function outboundClick(ctx, link, config) {
    var kind = linkKind(link.url, config);
    if (!kind) return null;
    return {
      name: 'docs_outbound_click',
      params: withAttribution({
        page_path: clip(ctx.path),
        client: clientFor(link.headings, config, ctx.pageClient),
        link_kind: kind,
        link_url: cleanUrl(link.url)
      }, ctx.attribution, config)
    };
  }

  var api = {
    isTracked: isTracked,
    guideOf: guideOf,
    clientName: clientName,
    clientFor: clientFor,
    hashClient: hashClient,
    snippetKind: snippetKind,
    cleanUrl: cleanUrl,
    linkKind: linkKind,
    referrerHost: referrerHost,
    captureAttribution: captureAttribution,
    firstTouch: firstTouch,
    guideView: guideView,
    snippetCopy: snippetCopy,
    outboundClick: outboundClick
  };
  if (typeof module !== 'undefined' && module.exports) { module.exports = api; return; }

  // DOM wiring.
  var data = document.getElementById('docs-events');
  if (!data) return;
  var config;
  try { config = JSON.parse(data.textContent); } catch (e) { return; }
  var loc = window.location;
  var tracked = isTracked(loc.pathname, config.pages);
  var pageClient = data.getAttribute('data-mcp-client') || '';
  var started = false;
  var ctx;

  function consented() {
    try { return localStorage.getItem(config.consent_key) === 'granted'; } catch (e) { return false; }
  }

  function attribution() {
    var stored = null;
    try { stored = JSON.parse(sessionStorage.getItem(config.storage_key) || 'null'); } catch (e) { stored = null; }
    var kept = firstTouch(stored, captureAttribution(loc.search, document.referrer, loc.host, loc.pathname, config, tracked));
    try { sessionStorage.setItem(config.storage_key, JSON.stringify(kept)); } catch (e) { /* private mode */ }
    return kept;
  }

  function send(event) {
    if (!event || !consented() || typeof window.gtag !== 'function') return;
    window.gtag('event', event.name, event.params);
  }

  function headingsBefore(el) {
    var all = document.querySelectorAll('h2[id], h3[id]');
    var out = [];
    for (var i = 0; i < all.length; i++) {
      // 4 is Node.DOCUMENT_POSITION_FOLLOWING: el comes after the heading.
      if (all[i].compareDocumentPosition(el) & 4) {
        out.push({ level: Number(all[i].tagName.charAt(1)), id: all[i].id });
      }
    }
    return out;
  }

  function onClick(event) {
    if (event.type === 'auxclick' && event.button !== 1) return;
    var target = event.target;
    if (!target || typeof target.closest !== 'function') return;
    var copy = target.closest('.term-copy');
    if (copy) {
      // A middle-click on Copy copies nothing.
      if (event.type !== 'click') return;
      var card = copy.closest('.term');
      if (!card) return;
      var title = card.querySelector('.term-title');
      send(snippetCopy(ctx, {
        lang: card.getAttribute('data-lang'),
        title: title ? title.textContent : '',
        headings: headingsBefore(card)
      }, config));
      return;
    }
    var a = target.closest('a[href]');
    if (!a) return;
    var url;
    try { url = new URL(a.getAttribute('href'), loc.href); } catch (e) { return; }
    send(outboundClick(ctx, { url: url, headings: headingsBefore(a) }, config));
  }

  function start() {
    if (started || !consented()) return;
    started = true;
    var first = attribution();
    if (!tracked || typeof window.gtag !== 'function') return;
    ctx = { path: loc.pathname, hash: loc.hash, pageClient: pageClient, attribution: first };
    send(guideView(ctx, config));
    document.addEventListener('click', onClick, true);
    document.addEventListener('auxclick', onClick, true);
  }

  start();
  if (!started) document.addEventListener(config.consent_event, start);
})();
