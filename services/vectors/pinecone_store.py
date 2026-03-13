from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

from core.utils.optional_imports import optional_import

pinecone, _ = optional_import("pinecone")

from .abstraction import IVectorStore


class PineconeVectorStore(IVectorStore):
    def __init__(self, api_key: str, environment: Optional[str], index_name: str) -> None:
        if pinecone is None:  # pragma: no cover - optional
            raise RuntimeError("pinecone-client is not installed")
        pinecone.init(api_key=api_key, environment=environment or None)
        self._index = pinecone.Index(index_name)

    async def upsert(self, items: List[Tuple[str, List[float], Dict[str, Any]]]) -> None:
        vectors = [{"id": _id, "values": vec, "metadata": meta} for _id, vec, meta in items]
        self._index.upsert(vectors=vectors)

    async def query(self, vector: List[float], *, top_k: int = 5) -> List[Dict[str, Any]]:
        res = self._index.query(vector=vector, top_k=top_k, include_metadata=True)
        out: List[Dict[str, Any]] = []
        for match in res.matches or []:
            out.append(
                {
                    "id": match.id,
                    "score": match.score,
                    "metadata": match.metadata or {},
                }
            )
        return out


__all__ = ["PineconeVectorStore"]

