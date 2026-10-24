#!/usr/bin/env python3
"""Regression tests for the perfume domain model."""

import unittest

from domain.models import Perfume


class PerfumeModelTests(unittest.TestCase):
    def test_product_dict_preserves_expected_ui_shape(self):
        perfume = Perfume(
            id=1,
            name="Rose Example",
            gender="Woman",
            intensity="Light",
            notes=["Rose"],
            season="Summer",
            concept="Daily",
            classification="Floral",
            longevity="Moderate",
            collection="Classic",
            desc="Classic - Floral - Rose",
        )

        self.assertEqual(
            perfume.to_product_dict(),
            {
                "id": 1,
                "name": "Rose Example",
                "gender": "Woman",
                "intensity": "Light",
                "notes": ["Rose"],
                "season": "Summer",
                "concept": "Daily",
                "classification": "Floral",
                "longevity": "Moderate",
                "collection": "Classic",
                "desc": "Classic - Floral - Rose",
            },
        )


if __name__ == "__main__":
    unittest.main()
