#!/usr/bin/env python3
"""Header menu behaviour (assets/js/nav.js, issue #550): moving between sibling
groups swaps the panel in one step, with no zero-open frame, never two panels
open at once, and no enter animation replay.

Runs the real script in nav_harness.js's fake DOM. Run with `make test-scripts`
(CI runs it too).
"""

import json
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
NAV_JS = ROOT / "assets/js/nav.js"
HARNESS = Path(__file__).resolve().parent / "nav_harness.js"


def run_nav(steps: list, **extra) -> dict:
    scenario = dict(extra, steps=steps)
    result = subprocess.run(
        ["node", str(HARNESS), str(NAV_JS), json.dumps(scenario)],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(f"nav.js harness failed: {result.stderr.strip()}")
    return json.loads(result.stdout)


def after(samples: list, index: int) -> list:
    """Samples taken from step `index` on (each step and its timers)."""
    return [s for s in samples if int(s["after"].split(":")[0]) >= index]


def enter(i): return {"do": "enter", "id": i}
def leave(i): return {"do": "leave", "id": i}
def wait(ms): return {"do": "wait", "ms": ms}
def focus(i): return {"do": "focus", "id": i}


# A cold hover waits 90ms; this opens `product` and settles.
OPEN_PRODUCT = [enter("product"), wait(100)]


class NavTest(unittest.TestCase):
    def assertNeverGapped(self, samples: list, start: int, msg: str = ""):
        for s in after(samples, start):
            self.assertGreaterEqual(s["openCount"], 1, f"zero-open frame at {s['after']} {msg}")
            self.assertLessEqual(s["openCount"], 1, f"two panels open at {s['after']} {msg}")
            self.assertFalse(s["mismatch"], f"is-open and aria-expanded disagree at {s['after']}")

    def test_cold_open_waits_and_does_not_mark_swap(self):
        out = run_nav([enter("product")])
        self.assertEqual(out["openCount"], 0, "a cold hover must wait for its delay")
        out = run_nav(OPEN_PRODUCT)
        self.assertEqual(out["openIds"], ["product"])
        self.assertFalse(out["swap"], "a cold open animates, so it is not a swap")

    def test_fast_pointer_siblings_never_gap(self):
        steps = OPEN_PRODUCT + [
            leave("product"), enter("platforms"),
            leave("platforms"), enter("resources"),
            leave("resources"), enter("product"),
        ]
        out = run_nav(steps)
        self.assertEqual(out["openIds"], ["product"])
        self.assertNeverGapped(out["samples"], 2)
        first_hop = [s for s in out["samples"] if s["after"] == "3:enter:platforms"][0]
        self.assertTrue(first_hop["swap"], "the first sibling hop marks the swap")
        self.assertTrue(out["swap"])

    def test_sibling_hop_leaves_exactly_the_target_open(self):
        out = run_nav(OPEN_PRODUCT + [leave("product"), enter("platforms")])
        self.assertEqual(out["openIds"], ["platforms"])
        # The pending close timer of the group left behind must not fire later.
        out = run_nav(OPEN_PRODUCT + [leave("product"), enter("platforms"), wait(500)])
        self.assertEqual(out["openIds"], ["platforms"])
        self.assertNeverGapped(out["samples"], 2)

    def test_rapid_reversals_never_gap(self):
        steps = OPEN_PRODUCT + [
            leave("product"), enter("platforms"),
            leave("platforms"), enter("product"),
            leave("product"), enter("platforms"),
            wait(300),
        ]
        out = run_nav(steps)
        self.assertEqual(out["openIds"], ["platforms"])
        self.assertNeverGapped(out["samples"], 2)

    def test_click_between_groups_never_gaps(self):
        out = run_nav([{"do": "click", "id": "product"}, {"do": "click", "id": "platforms"}])
        self.assertEqual(out["openIds"], ["platforms"])
        self.assertNeverGapped(out["samples"], 0)
        self.assertTrue(out["swap"])

    def test_keyboard_focus_between_triggers_never_gaps(self):
        steps = [focus("product"), {"do": "click", "id": "product"}, focus("platforms"), focus("resources")]
        out = run_nav(steps)
        self.assertEqual(out["openIds"], ["resources"])
        self.assertNeverGapped(out["samples"], 1)

    def test_escape_closes_to_zero_and_clears_swap(self):
        out = run_nav(OPEN_PRODUCT + [leave("product"), enter("platforms"), {"do": "escape"}])
        self.assertEqual(out["openCount"], 0)
        self.assertFalse(out["swap"], "the next open is cold again")

    def test_outside_click_closes_to_zero(self):
        out = run_nav(OPEN_PRODUCT + [{"do": "outside"}])
        self.assertEqual(out["openCount"], 0)
        self.assertFalse(out["swap"])

    def test_leaving_closes_after_delay(self):
        out = run_nav(OPEN_PRODUCT + [leave("product"), wait(100)])
        self.assertEqual(out["openIds"], ["product"], "closing waits 220ms")
        out = run_nav(OPEN_PRODUCT + [leave("product"), wait(300)])
        self.assertEqual(out["openCount"], 0)

    def test_narrow_viewport_hover_does_not_open(self):
        out = run_nav(OPEN_PRODUCT, wide=False)
        self.assertEqual(out["openCount"], 0)


if __name__ == "__main__":
    unittest.main()
