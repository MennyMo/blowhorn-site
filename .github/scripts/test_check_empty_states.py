#!/usr/bin/env python3
"""Every empty state carries its cast character: the built copy must sit in
a cast-empty block with art, and the search template needs art and a query
slot. Run with `make test-scripts` (CI runs it too).
"""

import unittest

import check_empty_states as check

ART = '<img class="cast-empty-art" src="/assets/brand/cast/robo-recruit-base.webp" alt="">'


def block(copy, art=ART):
    return f'<div class="cast-empty">{art}<p class="cast-empty-text ui">{copy}</p></div>'


def template(art=ART, slot='<span data-cast-query></span>'):
    return (
        '<template id="cast-empty-search"><div class="cast-empty">'
        f'{art}<p class="cast-empty-text ui">No page matches "{slot}".</p></div></template>'
    )


class EveryEmptyStateHasACharacter(unittest.TestCase):
    def test_copy_with_art_passes(self):
        html = block("This example is coming soon.")
        self.assertEqual(check.problems_in("p", html), [])

    def test_copy_without_art_fails(self):
        html = block("This example is coming soon.", art="")
        self.assertEqual(
            check.problems_in("p", html),
            ["p: 'This example is coming soon.' is shown without its cast character"],
        )

    def test_copy_outside_a_block_fails(self):
        html = "<p>No actions match.</p>"
        self.assertEqual(
            check.problems_in("p", html),
            ["p: 'No actions match.' is shown outside a cast-empty block"],
        )

    def test_search_template_needs_art_and_query_slot(self):
        self.assertEqual(check.problems_in("p", template()), [])
        self.assertIn(
            "p: the search no-results template has no cast character",
            check.problems_in("p", template(art="")),
        )
        self.assertIn(
            "p: the search no-results template has no query slot",
            check.problems_in("p", template(slot="")),
        )

    def test_retired_copy_fails(self):
        html = "<p>No results found for query \"x\"</p>"
        self.assertEqual(
            check.problems_in("p", html),
            ["p: retired empty-state copy 'No results found for query'"],
        )

    def test_a_page_without_empty_states_passes(self):
        self.assertEqual(check.problems_in("p", "<main><p>Hello</p></main>"), [])


if __name__ == "__main__":
    unittest.main()
