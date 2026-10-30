#!/usr/bin/env node
/* Run assets/js/docs-attribution.js for test_docs_attribution.py, with the
   real data/docs_events.json.

   Usage: node docs_attribution_harness.js pure '<json calls>'
     calls: [{"fn": "linkKind", "args": [...]}, ...]; prints the results.
     The wrappers below parse URL strings and pass the config.
   Usage: node docs_attribution_harness.js page '<json scenario>'
     Runs the script's DOM wiring against a tiny fake page.
     scenario: { "url": "https://blowhorn.ai/docs/...?utm_source=x#claude-code",
       "referrer": "", "consent": null | "granted" | "denied",
       "session": {...} | null, "mcpClient": "", "partial": true,
       "nodes": [{"h": 2, "id": "..."}, {"card": "json", "title": "...", "name": "c1"},
                 {"a": "https://...", "name": "l1"}],
       "steps": [{"click": "c1"}, {"aux": "l1", "button": 1}, {"grant": true}] }
     Prints: { "after": [[gtag calls so far] per step, starting with load],
       "session": sessionStorage, "localWrites": keys written to localStorage }
     Off the tracked pages the page carries only CAPTURE_KEYS of the config,
     as layouts/_partials/docs-attribution.html emits it.
   Usage: node docs_attribution_harness.js consent '<json scenario>'
     Runs assets/js/consent.js. scenario: { "consent": null | "granted" | "denied",
       "session": {...}, "choose": "granted" | "denied" }
     Prints: { "session": sessionStorage, "consent": the stored choice } */
"use strict";
const fs = require("fs");
const path = require("path");
const vm = require("vm");

const ROOT = path.resolve(__dirname, "..", "..");
const SCRIPT = path.join(ROOT, "assets/js/docs-attribution.js");
const CONSENT = path.join(ROOT, "assets/js/consent.js");
// The config keys the partial emits on a page outside pages.
const CAPTURE_KEYS = ["pages", "consent_key", "consent_event", "storage_key", "internal_hosts", "utm_params", "attribution_params"];
const CONFIG = JSON.parse(fs.readFileSync(path.join(ROOT, "data/docs_events.json"), "utf8"));

function pure(calls) {
  const api = require(SCRIPT);
  const c = CONFIG;
  const link = (l) => ({ url: new URL(l.url), headings: l.headings || [] });
  const fns = {
    isTracked: (p) => api.isTracked(p, c.pages),
    guideOf: (p) => api.guideOf(p),
    clientFor: (headings, pageClient) => api.clientFor(headings, c, pageClient),
    hashClient: (hash, pageClient) => api.hashClient(hash, c, pageClient),
    snippetKind: (lang) => api.snippetKind(lang, c),
    cleanUrl: (href) => api.cleanUrl(new URL(href)),
    linkKind: (href, pageHost) => api.linkKind(new URL(href), pageHost, c),
    referrerHost: (ref, pageHost) => api.referrerHost(ref, pageHost, c),
    captureAttribution: (search, ref, host, p, tracked) => api.captureAttribution(search, ref, host, p, c, tracked),
    firstTouch: (stored, fresh) => api.firstTouch(stored, fresh),
    guideView: (ctx) => api.guideView(ctx, c),
    snippetCopy: (ctx, card) => api.snippetCopy(ctx, card, c),
    outboundClick: (ctx, l) => api.outboundClick(ctx, link(l), c),
  };
  return calls.map(({ fn, args }) => {
    if (!fns[fn]) throw new Error("harness: unknown fn " + fn);
    return fns[fn](...args);
  });
}

function storage(initial, writes) {
  const m = new Map(Object.entries(initial || {}));
  return {
    getItem: (k) => (m.has(k) ? m.get(k) : null),
    setItem: (k, v) => { if (writes) writes.push(k); m.set(k, String(v)); },
    set: (k, v) => m.set(k, v), // the harness's own write, not recorded
    dump: () => Object.fromEntries(m),
  };
}

class El {
  constructor(order, tag, attrs, classes, parent) {
    this.order = order;
    this.tagName = tag.toUpperCase();
    this.attrs = attrs || {};
    this.classes = classes || [];
    this.parentNode = parent || null;
    this.textContent = "";
    this.children = [];
    this.id = this.attrs.id || "";
  }
  getAttribute(n) { return n in this.attrs ? this.attrs[n] : null; }
  matches(sel) {
    if (sel === "a[href]") return this.tagName === "A" && "href" in this.attrs;
    if (sel.startsWith(".")) return this.classes.includes(sel.slice(1));
    throw new Error("harness: unsupported selector " + sel);
  }
  closest(sel) {
    for (let n = this; n; n = n.parentNode) if (n.matches(sel)) return n;
    return null;
  }
  querySelector(sel) { return this.children.find((ch) => ch.matches(sel)) || null; }
  compareDocumentPosition(other) { return other.order > this.order ? 4 : 2; }
}

function page(s) {
  const listeners = {};
  const calls = [];
  const localWrites = [];
  const url = new URL(s.url);
  const els = {};
  const headings = [];
  let order = 0;
  for (const n of s.nodes || []) {
    order += 1;
    if (n.h) {
      headings.push(new El(order, "h" + n.h, { id: n.id }));
    } else if (n.card) {
      const fig = new El(order, "figure", { "data-lang": n.card }, ["term"]);
      const title = new El(order, "span", {}, ["term-title"], fig);
      title.textContent = n.title || "";
      const btn = new El(order, "button", {}, ["term-copy"], fig);
      const svg = new El(order, "svg", {}, [], btn);
      fig.children.push(title, btn);
      els[n.name] = svg;
    } else if (n.a) {
      els[n.name] = new El(order, "a", { href: n.a });
    }
  }
  const api = require(SCRIPT);
  const emitted = api.isTracked(url.pathname, CONFIG.pages)
    ? CONFIG
    : Object.fromEntries(CAPTURE_KEYS.map((k) => [k, CONFIG[k]]));
  const data = s.partial === false ? null : {
    textContent: JSON.stringify(emitted),
    getAttribute: (k) => (k === "data-mcp-client" && s.mcpClient ? s.mcpClient : null),
  };
  const document = {
    referrer: s.referrer || "",
    getElementById: (id) => (id === "docs-events" ? data : null),
    querySelectorAll: (sel) => {
      if (sel !== "h2[id], h3[id]") throw new Error("harness: unsupported selector " + sel);
      return headings;
    },
    addEventListener: (type, fn) => { (listeners[type] = listeners[type] || []).push(fn); },
    dispatchEvent: (ev) => { (listeners[ev.type] || []).forEach((fn) => fn(ev)); },
  };
  const local = storage(s.consent ? { "blowhorn-consent": s.consent } : {}, localWrites);
  const session = storage(s.session ? { [CONFIG.storage_key]: JSON.stringify(s.session) } : {});
  const window = {
    location: { pathname: url.pathname, search: url.search, hash: url.hash, host: url.host, hostname: url.hostname, href: url.href },
    gtag: function () { calls.push(Array.from(arguments)); },
  };
  const ctx = vm.createContext({ window, document, localStorage: local, sessionStorage: session, URL, URLSearchParams, JSON });
  vm.runInContext(fs.readFileSync(SCRIPT, "utf8"), ctx);
  const snap = () => JSON.parse(JSON.stringify(calls));
  const after = [snap()];
  for (const step of s.steps || []) {
    if (step.grant) {
      local.set("blowhorn-consent", "granted");
      document.dispatchEvent({ type: CONFIG.consent_event });
    } else if (step.click || step.aux) {
      const type = step.click ? "click" : "auxclick";
      const target = els[step.click || step.aux];
      (listeners[type] || []).forEach((fn) => fn({ type, target, button: step.button || 0 }));
    }
    after.push(snap());
  }
  return { after, session: session.dump(), localWrites };
}

function consent(s) {
  const listeners = {};
  const notice = {
    hidden: true,
    addEventListener: (type, fn) => { (listeners[type] = listeners[type] || []).push(fn); },
    querySelector: () => ({ focus() {} }),
  };
  const local = storage(s.consent ? { "blowhorn-consent": s.consent } : {});
  const m = new Map(s.session ? [[CONFIG.storage_key, JSON.stringify(s.session)]] : []);
  const sessionStorage = {
    getItem: (k) => (m.has(k) ? m.get(k) : null),
    setItem: (k, v) => m.set(k, String(v)),
    removeItem: (k) => m.delete(k),
  };
  const document = {
    currentScript: { getAttribute: () => "G-TEST" },
    readyState: "complete",
    head: { appendChild() {} },
    createElement: () => ({}),
    getElementById: (id) => (id === "consent" ? notice : null),
    addEventListener() {},
    dispatchEvent() {},
  };
  const window = { gtag() {}, location: { reload() {} } };
  class CustomEvent { constructor(type, init) { this.type = type; this.detail = init && init.detail; } }
  const ctx = vm.createContext({ window, document, localStorage: local, sessionStorage, CustomEvent });
  vm.runInContext(fs.readFileSync(CONSENT, "utf8"), ctx);
  if (s.choose) {
    const button = { getAttribute: () => s.choose };
    (listeners.click || []).forEach((fn) => fn({ target: { closest: () => button } }));
  }
  return { session: Object.fromEntries(m), consent: local.getItem("blowhorn-consent") };
}

const [mode, arg] = process.argv.slice(2);
const input = JSON.parse(arg);
const run = { pure, page, consent }[mode];
if (!run) throw new Error("harness: unknown mode " + mode);
process.stdout.write(JSON.stringify(run(input)));
