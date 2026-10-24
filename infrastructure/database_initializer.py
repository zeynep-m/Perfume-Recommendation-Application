"""SQLite schema creation and initial perfume data loading."""

import json
import os
import sqlite3


class DatabaseInitializer:
    """Create the perfume schema and seed it from the bundled JSON data."""

    def __init__(self, db_name="perfumes.db", seed_file=None):
        self.db_name = db_name
        self.seed_file = seed_file or os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "perfumes.json",
        )

    def get_connection(self):
        return sqlite3.connect(self.db_name)

    def table_exists(self):
        """Return whether the perfumes table exists and contains data."""
        try:
            with self.get_connection() as conn:
                cur = conn.cursor()
                cur.execute(
                    "SELECT name FROM sqlite_master "
                    "WHERE type='table' AND name='perfumes'"
                )
                if cur.fetchone() is None:
                    return False
                cur.execute("SELECT COUNT(*) FROM perfumes")
                return cur.fetchone()[0] > 0
        except sqlite3.OperationalError:
            return False

    def initialize(self):
        """Initialize the database when the perfumes table is empty or absent."""
        if self.table_exists():
            return

        if not os.path.exists(self.seed_file):
            print(
                f"Warning: {self.seed_file} not found. "
                "Database cannot be initialized."
            )
            return

        with open(self.seed_file, "r") as file:
            perfumes_data = json.load(file)

        with self.get_connection() as conn:
            cur = conn.cursor()
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS gender_vocab (
                    id INTEGER PRIMARY KEY,
                    value TEXT UNIQUE NOT NULL
                )
                """
            )
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS classification_vocab (
                    id INTEGER PRIMARY KEY,
                    value TEXT UNIQUE NOT NULL
                )
                """
            )
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS season_vocab (
                    id INTEGER PRIMARY KEY,
                    value TEXT UNIQUE NOT NULL
                )
                """
            )
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS intensity_vocab (
                    id INTEGER PRIMARY KEY,
                    value TEXT UNIQUE NOT NULL
                )
                """
            )
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS perfumes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    perfume TEXT,
                    gender TEXT,
                    intensity TEXT,
                    ingredients_notes TEXT,
                    season TEXT,
                    concept TEXT,
                    longevity TEXT,
                    collection TEXT,
                    classification TEXT,
                    subfamily TEXT
                )
                """
            )

            for perfume in perfumes_data:
                try:
                    cur.execute(
                        "INSERT OR IGNORE INTO gender_vocab (value) VALUES (?)",
                        (perfume["Gender"],),
                    )
                    cur.execute(
                        "INSERT OR IGNORE INTO classification_vocab (value) VALUES (?)",
                        (perfume["Classification"],),
                    )
                    cur.execute(
                        "INSERT OR IGNORE INTO season_vocab (value) VALUES (?)",
                        (perfume["Season"],),
                    )
                    cur.execute(
                        "INSERT OR IGNORE INTO intensity_vocab (value) VALUES (?)",
                        (perfume["Intensity"],),
                    )
                except Exception:
                    pass

            for perfume in perfumes_data:
                cur.execute(
                    """
                    INSERT INTO perfumes (
                        perfume, gender, intensity, ingredients_notes,
                        season, concept, longevity, collection,
                        classification, subfamily
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        perfume["Perfume"],
                        perfume["Gender"],
                        perfume["Intensity"],
                        perfume["Ingredients_Notes"],
                        perfume["Season"],
                        perfume["Concept"],
                        perfume["Longevity"],
                        perfume["Collection"],
                        perfume["Classification"],
                        perfume["Subfamily"],
                    ),
                )

            conn.commit()
            print("Database initialized from perfumes.json with controlled vocabularies")
