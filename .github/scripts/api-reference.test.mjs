// Behavioural test for assets/js/api-reference.js: a malformed #fragment must be
// ignored, a valid one must still open its operation. Run by
// test_api_reference_viewer.py (make test-scripts). Fake DOM, no dependencies.
import test from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import vm from "node:vm";

const source = fs.readFileSync(new URL("../../assets/js/api-reference.js", import.meta.url), "utf8");

function run(hash) {
  const op = { hidden: false, open: false, scrolled: false,
    scrollIntoView() { this.scrolled = true; }, closest() { return op; } };
  const target = { closest() { return op; } };
  const listeners = {};
  const el = (extra) => Object.assign({ hidden: true, textContent: "", value: "",
    addEventListener() {}, setAttribute() {}, querySelector() { return null; } }, extra);
  const root = el({
    querySelector: () => el(),
    querySelectorAll: (sel) => (sel === "[data-api-op]" ? [op] : []),
    contains: () => true,
  });
  const window = { location: { hash }, addEventListener: (n, f) => { listeners[n] = f; } };
  const document = {
    querySelector: () => root,
    getElementById: (id) => (id === "op-ok" ? target : null),
  };
  vm.runInNewContext(source, { window, document });
  return op;
}

test("a valid fragment opens its operation", () => {
  const op = run("#op-ok");
  assert.equal(op.open, true);
  assert.equal(op.scrolled, true);
});

for (const hash of ["#%", "#%E0%A4%A", "#%FF", "#op-ok%"]) {
  test(`malformed fragment ${hash} is ignored without throwing`, () => {
    const op = run(hash);
    assert.equal(op.open, false);
    assert.equal(op.scrolled, false);
  });
}
