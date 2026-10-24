"""SQLite persistence operations for perfumes."""

import sqlite3


class PerfumeRepository:
    """Repository responsible for querying and changing perfume records."""

    def __init__(self, db_name="perfumes.db"):
        self.db_name = db_name

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

    def get_perfumes(self):
        """Retrieve all perfumes from the database."""
        with self.get_connection() as conn:
            cur = conn.cursor()
            cur.execute(
                "SELECT id, perfume, gender, intensity, ingredients_notes, "
                "collection, season, concept, classification, longevity "
                "FROM perfumes"
            )
            return cur.fetchall()

    def get_perfume_details(self, perfume_id):
        """Retrieve full details of a specific perfume."""
        with self.get_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM perfumes WHERE id=?", (perfume_id,))
            return cur.fetchone()

    def get_total_count(self):
        """Get total number of perfumes in the database."""
        with self.get_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT COUNT(*) FROM perfumes")
            return cur.fetchone()[0]

    def delete_perfume(self, perfume_id):
        """Delete a perfume by ID."""
        with self.get_connection() as conn:
            cur = conn.cursor()
            cur.execute("DELETE FROM perfumes WHERE id=?", (perfume_id,))

    def update_perfume(
        self,
        perfume_id,
        perfume,
        gender,
        intensity,
        ingredients_notes,
        season,
        concept,
        longevity,
        collection,
        classification,
        subfamily,
    ):
        """Update a perfume record."""
        with self.get_connection() as conn:
            cur = conn.cursor()
            cur.execute(
                """
                UPDATE perfumes
                SET perfume=?, gender=?, intensity=?, ingredients_notes=?,
                    season=?, concept=?, longevity=?, collection=?,
                    classification=?, subfamily=?
                WHERE id=?
                """,
                (
                    perfume,
                    gender,
                    intensity,
                    ingredients_notes,
                    season,
                    concept,
                    longevity,
                    collection,
                    classification,
                    subfamily,
                    perfume_id,
                ),
            )

    def add_perfume(
        self,
        perfume,
        gender,
        intensity,
        ingredients_notes,
        season,
        concept,
        longevity,
        collection,
        classification,
        subfamily,
    ):
        """Add a new perfume."""
        with self.get_connection() as conn:
            cur = conn.cursor()
            cur.execute(
                """
                INSERT INTO perfumes (
                    perfume, gender, intensity, ingredients_notes,
                    season, concept, longevity, collection,
                    classification, subfamily
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    perfume,
                    gender,
                    intensity,
                    ingredients_notes,
                    season,
                    concept,
                    longevity,
                    collection,
                    classification,
                    subfamily,
                ),
            )

    def search_perfumes(self, search_term):
        """Search perfumes by name, gender, classification, notes, or season."""
        with self.get_connection() as conn:
            cur = conn.cursor()
            query = """
                SELECT id, perfume, gender, intensity, ingredients_notes,
                       collection, season, concept, classification, longevity
                FROM perfumes
                WHERE perfume LIKE ? OR gender LIKE ? OR classification LIKE ?
                   OR ingredients_notes LIKE ? OR season LIKE ?
            """
            search_param = f"%{search_term}%"
            cur.execute(
                query,
                (search_param, search_param, search_param, search_param, search_param),
            )
            return cur.fetchall()

    def get_statistics(self):
        """Get aggregate statistics about perfumes."""
        with self.get_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT COUNT(*) FROM perfumes")
            total = cur.fetchone()[0]
            cur.execute(
                "SELECT gender, COUNT(*) FROM perfumes "
                "GROUP BY gender ORDER BY COUNT(*) DESC"
            )
            gender_counts = cur.fetchall()
            cur.execute(
                "SELECT intensity, COUNT(*) FROM perfumes "
                "GROUP BY intensity ORDER BY COUNT(*) DESC"
            )
            intensity_counts = cur.fetchall()
            cur.execute(
                "SELECT classification, COUNT(*) FROM perfumes "
                "GROUP BY classification ORDER BY COUNT(*) DESC LIMIT 5"
            )
            classification_counts = cur.fetchall()
            return {
                "total": total,
                "gender": gender_counts,
                "intensity": intensity_counts,
                "classification": classification_counts,
            }

    def get_vocab(self, vocab_type):
        """Get a controlled vocabulary list for dropdowns."""
        table_map = {
            "gender": "gender_vocab",
            "classification": "classification_vocab",
            "season": "season_vocab",
            "intensity": "intensity_vocab",
        }
        table_name = table_map.get(vocab_type)
        if not table_name:
            return []
        with self.get_connection() as conn:
            cur = conn.cursor()
            cur.execute(f"SELECT value FROM {table_name} ORDER BY value")
            return [row[0] for row in cur.fetchall()]
