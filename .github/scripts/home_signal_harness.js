#!/usr/bin/env node
/* Run assets/js/home-signal.js against a tiny fake DOM and report what the
   platforms section shows. Used by test_themes.py, so the test checks what
   the script does, not what its source text says.

   Usage: node home_signal_harness.js SCRIPT '<json scenario>'
   Scenario: { "tabs": ["category", ...], "on": "category" | "",
               "hash": "#plat-panel-action", "click": "role", "key": "ArrowRight" }
   Prints: { "tab": <selected tab id>, "panels": {id: not hidden}, "ariaSelected": [...] } */
"use strict";
const fs = require("fs");
const vm = require("vm");

class ClassList {
  constructor() { this.set = new Set(); }
  add(c) { this.set.add(c); }
  remove(c) { this.set.delete(c); }
  contains(c) { return this.set.has(c); }
  toggle(c, force) {
    const on = force === undefined ? !this.set.has(c) : !!force;
    if (on) this.set.add(c); else this.set.delete(c);
    return on;
  }
}

function parseSelector(sel) {
  const parts = [];
  const re = /\[([a-z-]+)(?:="([^"]*)")?\]|\.([a-z-]+)|:not\(\[([a-z-]+)\]\)/gy;
  let m;
  while ((m = re.exec(sel))) {
    if (m[1]) parts.push({ attr: m[1], value: m[2] });
    else if (m[3]) parts.push({ cls: m[3] });
    else parts.push({ notAttr: m[4] });
    if (re.lastIndex === sel.length) return parts;
  }
  throw new Error("harness: unsupported selector " + sel);
}

class El {
  constructor(attrs, classes) {
    this.attrs = Object.assign({}, attrs || {});
    this.classList = new ClassList();
    (classes || []).forEach((c) => this.classList.add(c));
    this.children = [];
    this.listeners = {};
    this.hidden = false;
    this.tabIndex = 0;
    this.id = this.attrs.id || "";
    const style = {};
    this.style = { setProperty: (k, v) => { style[k] = v; } };
  }
  append(child) { this.children.push(child); return child; }
  getAttribute(n) { return Object.prototype.hasOwnProperty.call(this.attrs, n) ? this.attrs[n] : null; }
  setAttribute(n, v) { this.attrs[n] = String(v); }
  hasAttribute(n) { return Object.prototype.hasOwnProperty.call(this.attrs, n); }
  addEventListener(t, fn) { (this.listeners[t] = this.listeners[t] || []).push(fn); }
  dispatch(t, extra) {
    const ev = Object.assign({ preventDefault() {} }, extra || {});
    (this.listeners[t] || []).forEach((fn) => fn(ev));
  }
  focus() {}
  matches(sel) {
    return parseSelector(sel).every((p) => {
      if (p.cls) return this.classList.contains(p.cls);
      if (p.notAttr) return !(p.notAttr === "hidden" ? this.hidden : this.hasAttribute(p.notAttr));
      if (!this.hasAttribute(p.attr)) return false;
      return p.value === undefined || this.attrs[p.attr] === p.value;
    });
  }
  descendants() {
    const out = [];
    const walk = (el) => el.children.forEach((c) => { out.push(c); walk(c); });
    walk(this);
    return out;
  }
  querySelectorAll(sel) {
    const found = this.descendants().filter((el) => el.matches(sel));
    found.forEach = Array.prototype.forEach;
    return found;
  }
  querySelector(sel) { return this.querySelectorAll(sel)[0] || null; }
}

function build(scenario) {
  const doc = new El();
  const section = doc.append(new El({ id: "platforms", "data-platforms": "" }));
  scenario.tabs.forEach((id) => {
    const on = id === scenario.on;
    section.append(new El({ id: "plat-tab-" + id, "data-plat-tab": id, "aria-selected": on ? "true" : "false" }, on ? ["plat-tab", "is-on"] : ["plat-tab"]));
  });
  scenario.tabs.forEach((id) => {
    section.append(new El({ id: "plat-panel-" + id, "data-plat-panel": id }, id === scenario.on ? ["plat-panel", "is-on"] : ["plat-panel"]));
  });
  doc.getElementById = (id) => doc.descendants().find((el) => el.id === id) || null;
  return { doc, section };
}

function main() {
  const [script, raw] = process.argv.slice(2);
  const scenario = JSON.parse(raw);
  const { doc, section } = build(scenario);
  const window = {
    location: { hash: scenario.hash || "" },
    matchMedia: () => ({ matches: true }),
    setTimeout: () => 0,
  };
  const ctx = { window, document: doc, IntersectionObserver: function () {} };
  vm.runInNewContext(fs.readFileSync(script, "utf8"), ctx, { filename: script });
  const tabOf = (id) => section.querySelector('[data-plat-tab="' + id + '"]');
  if (scenario.click) tabOf(scenario.click).dispatch("click");
  if (scenario.key) {
    const on = section.querySelector("[data-plat-tab].is-on");
    on.dispatch("keydown", { key: scenario.key });
  }
  const panels = {};
  section.querySelectorAll("[data-plat-panel]").forEach((p) => {
    panels[p.getAttribute("data-plat-panel")] = !p.hidden;
  });
  const on = section.querySelectorAll("[data-plat-tab].is-on").map((t) => t.getAttribute("data-plat-tab"));
  const ariaSelected = section.querySelectorAll("[data-plat-tab]")
    .filter((t) => t.getAttribute("aria-selected") === "true")
    .map((t) => t.getAttribute("data-plat-tab"));
  process.stdout.write(JSON.stringify({ tab: on.length === 1 ? on[0] : on, panels, ariaSelected, enhanced: section.classList.contains("is-plat-enhanced") }));
}

main();
