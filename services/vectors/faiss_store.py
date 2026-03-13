from __future__ import annotations

from typing import Any, Dict, List, Tuple

from core.utils.optional_imports import optional_import

faiss, _ = optional_import("faiss")
np, _ = optional_import("numpy")

from .abstraction import IVectorStore


class FaissVectorStore(IVectorStore):
    """
    Simple in-memory FAISS vector store.

    This implementation keeps all vectors in memory and rebuilds the
    underlying index on each upsert, which is fine for development or
    small datasets. Projects that need more advanced FAISS usage can
    extend or replace this implementation.
    """

    def __init__(self) -> None:
        if faiss is None or np is None:  # pragma: no cover - optional
            raise RuntimeError("faiss (and numpy) are not installed")
        self._index = None
        self._ids: List[str] = []
        self._dim: int | None = None

    async def upsert(self, items: List[Tuple[str, List[float], Dict[str, Any]]]) -> None:
        if not items:
            return
        # Determine dimension from first vector
        dim = len(items[0][1])
        self._dim = dim
        self._ids = [item_id for item_id, _, _ in items]
        vectors = np.array([vec for _, vec, _ in items], dtype="float32")
        index = faiss.IndexFlatL2(dim)
        index.add(vectors)
        self._index = index

    async def query(self, vector: List[float], *, top_k: int = 5) -> List[Dict[str, Any]]:
        if self._index is None or self._dim is None or not self._ids:
            return []
        q = np.array([vector], dtype="float32")
        distances, indices = self._index.search(q, top_k)
        results: List[Dict[str, Any]] = []
        for dist, idx in zip(distances[0], indices[0]):
            if idx < 0 or idx >= len(self._ids):
                continue
            results.append(
                {
                    "id": self._ids[idx],
                    "score": float(dist),
                    "metadata": {},
                }
            )
        return results


__all__ = ["FaissVectorStore"]

