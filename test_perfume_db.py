#!/usr/bin/env python3
"""Regression tests for the SQLite perfume database."""

import tempfile
import unittest
from pathlib import Path

from infrastructure import PerfumeRepositoryProtocol
from infrastructure.perfume_repository import PerfumeRepository
from perfume_db import PerfumeDatabase


class PerfumeDatabaseTests(unittest.TestCase):
    def setUp(self):
        self.temp_directory = tempfile.TemporaryDirectory()
        database_path = Path(self.temp_directory.name) / "test-perfumes.db"
        self.database = PerfumeDatabase(str(database_path))

    def tearDown(self):
        self.temp_directory.cleanup()

    def test_initializes_from_seed_data(self):
        self.assertTrue(self.database.table_exists())
        self.assertEqual(self.database.get_total_count(), 76)
        self.assertEqual(len(self.database.get_perfumes()), 76)

    def test_add_update_and_delete_perfume(self):
        original_count = self.database.get_total_count()
        self.database.add_perfume(
            perfume="Test Perfume",
            gender="Unisex",
            intensity="Light",
            ingredients_notes="Rose, Jasmine",
            season="Spring",
            concept="Daily",
            longevity="Moderate",
            collection="Test Collection",
            classification="Floral",
            subfamily="Test Subfamily",
        )

        self.assertEqual(self.database.get_total_count(), original_count + 1)
        created = self.database.search_perfumes("Test Perfume")
        self.assertEqual(len(created), 1)
        perfume_id = created[0][0]

        self.database.update_perfume(
            perfume_id=perfume_id,
            perfume="Updated Perfume",
            gender="Woman",
            intensity="Intense",
            ingredients_notes="Vanilla",
            season="Winter",
            concept="Night Out",
            longevity="Long",
            collection="Updated Collection",
            classification="Gourmand",
            subfamily="Updated Subfamily",
        )
        self.assertEqual(len(self.database.search_perfumes("Updated Perfume")), 1)
        self.assertEqual(len(self.database.search_perfumes("Test Perfume")), 0)

        self.database.delete_perfume(perfume_id)
        self.assertEqual(self.database.get_total_count(), original_count)

    def test_search_and_statistics_return_expected_shapes(self):
        results = self.database.search_perfumes("Rose")
        self.assertTrue(results)
        self.assertEqual(len(results[0]), 10)

        statistics = self.database.get_statistics()
        self.assertEqual(statistics["total"], 76)
        self.assertIn("gender", statistics)
        self.assertIn("intensity", statistics)
        self.assertIn("classification", statistics)

    def test_controlled_vocabularies_are_available(self):
        for vocabulary in ("gender", "classification", "season", "intensity"):
            values = self.database.get_vocab(vocabulary)
            self.assertTrue(values)
            self.assertEqual(values, sorted(values))

        self.assertEqual(self.database.get_vocab("unknown"), [])

    def test_repository_implements_persistence_contract(self):
        self.assertIsInstance(self.database, PerfumeRepositoryProtocol)
        self.assertIsInstance(PerfumeRepository(str(self.database.db_name)), PerfumeRepositoryProtocol)


if __name__ == "__main__":
    unittest.main()
