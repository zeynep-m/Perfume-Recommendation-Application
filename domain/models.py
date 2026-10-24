"""Domain models used to move perfume data between application layers."""

from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class Perfume:
    """Normalized perfume data used by the recommendation application."""

    id: int
    name: str
    gender: str
    intensity: str
    notes: list[str]
    season: str
    concept: str
    classification: str
    longevity: str
    collection: str
    desc: str

    def to_product_dict(self):
        """Return the legacy product shape used by the current UI."""
        return asdict(self)
