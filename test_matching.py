#!/usr/bin/env python3
"""Regression tests for recommendation matching behavior."""

import unittest

from domain.matching import (
    filter_rank_products,
    match_score,
    matches_notes,
    parse_selected_notes,
)


PRODUCT = {
    "name": "Rose Example",
    "gender": "Woman",
    "intensity": "Light",
    "season": "Summer",
    "concept": "Daily",
    "longevity": "Moderate",
    "notes": ["Rose", "Jasmine"],
}

PROFILE = {
    "gender": "Woman",
    "intensity": "Light",
    "season": "Summer",
    "concept": "Daily",
    "longevity": "Moderate",
}


class MatchingBehaviorTests(unittest.TestCase):
    def test_parse_selected_notes_trims_empty_values(self):
        self.assertEqual(
            parse_selected_notes(" rose, , jasmine "),
            ["rose", "jasmine"],
        )

    def test_matches_notes_supports_strict_and_non_strict_modes(self):
        self.assertTrue(matches_notes(PRODUCT["notes"], ["rose", "jasm"], strict=True))
        self.assertFalse(matches_notes(PRODUCT["notes"], ["rose", "vanilla"], strict=True))
        self.assertTrue(matches_notes(PRODUCT["notes"], ["rose", "vanilla"], strict=False))

    def test_exact_profile_is_tier_one(self):
        self.assertEqual(match_score(PRODUCT, PROFILE, ["rose"]), (1, 5, 5, 100))

    def test_non_matching_notes_filter_product_out(self):
        self.assertIsNone(match_score(PRODUCT, PROFILE, ["vanilla"]))

    def test_best_match_sorting_is_preserved(self):
        weaker_product = {**PRODUCT, "name": "Weaker", "intensity": "Intense"}
        results = filter_rank_products(
            PROFILE,
            "",
            "Best match",
            [weaker_product, PRODUCT],
            lambda value: value,
        )
        self.assertEqual([product["name"] for product in results], ["Rose Example", "Weaker"])


if __name__ == "__main__":
    unittest.main()
