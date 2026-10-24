"""Executable entry point for the perfume recommendation application."""

from app import PerfumeApplication, main
from domain.matching import match_score, matches_notes, parse_selected_notes
from domain.matching import filter_rank_products as _filter_rank_products
from i18n import _


def filter_rank_products(profile, notes_input, sort_mode, products, strict_notes=True):
    """Preserve the legacy helper signature for existing integrations."""
    return _filter_rank_products(
        profile,
        notes_input,
        sort_mode,
        products,
        _,
        strict_notes=strict_notes,
    )

__all__ = [
    "PerfumeApplication",
    "filter_rank_products",
    "main",
    "match_score",
    "matches_notes",
    "parse_selected_notes",
]


if __name__ == "__main__":
    main()
