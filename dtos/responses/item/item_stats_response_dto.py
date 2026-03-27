"""Item statistics response DTO."""

from __future__ import annotations

from typing import Self

from dtos.responses.I import IResponseDTO


class ItemStatsResponseDTO(IResponseDTO):
    """DTO for item statistics response."""

    transactionUrn: str = ""
    status: str = "SUCCESS"
    responseMessage: str = "Success"
    responseKey: str = "success"
    data: list | dict | None = None
    errors: list | dict | None = None
    total: int
    completed: int
    pending: int
    completion_rate: float

    def to_dict(self) -> dict:
        return {
            "total": self.total,
            "completed": self.completed,
            "pending": self.pending,
            "completion_rate": round(self.completion_rate, 2),
        }

    @classmethod
    def from_stats(cls, stats: dict) -> Self:
        return cls(
            total=stats.get("total", 0),
            completed=stats.get("completed", 0),
            pending=stats.get("pending", 0),
            completion_rate=stats.get("completion_rate", 0.0),
        )
