"""Item list response DTO."""

from __future__ import annotations

from typing import Self

from dtos.responses.I import IResponseDTO

from dtos.responses.item.item_response_dto import ItemResponseDTO


class ItemListResponseDTO(IResponseDTO):
    """DTO for list-of-items response."""

    transactionUrn: str = ""
    status: str = "SUCCESS"
    responseMessage: str = "Success"
    responseKey: str = "success"
    data: list | dict | None = None
    errors: list | dict | None = None
    items: list[ItemResponseDTO]
    total: int = 0
    completed_count: int = 0
    pending_count: int = 0

    def to_dict(self) -> dict:
        return {
            "items": [item.to_dict() for item in self.items],
            "total": self.total,
            "completed_count": self.completed_count,
            "pending_count": self.pending_count,
        }

    @classmethod
    def from_entities(cls, entities: list) -> Self:
        items = [ItemResponseDTO.from_entity(e) for e in entities]
        completed = sum(1 for e in entities if e.completed)
        return cls(
            items=items,
            total=len(items),
            completed_count=completed,
            pending_count=len(items) - completed,
        )
