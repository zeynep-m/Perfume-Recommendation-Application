"""Persistence contracts used by application services and views."""

from typing import Any, Protocol, Sequence, runtime_checkable


@runtime_checkable
class PerfumeRepositoryProtocol(Protocol):
    """Interface required by code that reads and changes perfume records."""

    def get_perfumes(self) -> Sequence[tuple[Any, ...]]:
        ...

    def get_perfume_details(self, perfume_id: int) -> tuple[Any, ...] | None:
        ...

    def get_total_count(self) -> int:
        ...

    def delete_perfume(self, perfume_id: int) -> None:
        ...

    def update_perfume(
        self,
        perfume_id: int,
        perfume: str,
        gender: str,
        intensity: str,
        ingredients_notes: str,
        season: str,
        concept: str,
        longevity: str,
        collection: str,
        classification: str,
        subfamily: str,
    ) -> None:
        ...

    def add_perfume(
        self,
        perfume: str,
        gender: str,
        intensity: str,
        ingredients_notes: str,
        season: str,
        concept: str,
        longevity: str,
        collection: str,
        classification: str,
        subfamily: str,
    ) -> None:
        ...

    def search_perfumes(self, search_term: str) -> Sequence[tuple[Any, ...]]:
        ...

    def get_statistics(self) -> dict[str, Any]:
        ...

    def get_vocab(self, vocab_type: str) -> list[str]:
        ...
