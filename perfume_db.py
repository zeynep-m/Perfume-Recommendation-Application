"""Backward-compatible database facade for the perfume application."""

from infrastructure.database_initializer import DatabaseInitializer
from infrastructure.perfume_repository import PerfumeRepository


class PerfumeDatabase(PerfumeRepository):
    """Compatibility facade combining initialization with repository access."""

    def __init__(self, db_name="perfumes.db"):
        super().__init__(db_name)
        self.initialize_database()

    def initialize_database(self):
        """Initialize the database through the dedicated initializer."""
        DatabaseInitializer(self.db_name).initialize()
