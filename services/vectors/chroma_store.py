from __future__ import annotations

from typing import Any, Dict, List, Tuple

from core.utils.optional_imports import optional_import

chromadb, _ = optional_import("chromadb")

from .abstraction import IVectorStore


class ChromaVectorStore(IVectorStore):
    """
    Simple ChromaDB-backed vector store.

    This implementation creates (or opens) a local persistent Chroma
    collection named "fastmvc" by default. For production, you can
    extend this to configure collections and client options.
    """

    def __init__(self, persist_directory: str) -> None:
        if chromadb is None:  # pragma: no cover - optional
            raise RuntimeError("chromadb is not installed")
        client = chromadb.PersistentClient(path=persist_directory)
        self._collection = client.get_or_create_collection("fastmvc")

    async def upsert(self, items: List[Tuple[str, List[float], Dict[str, Any]]]) -> None:
        if not items:
            return
        ids = [item_id for item_id, _, _ in items]
        embeddings = [vec for _, vec, _ in items]
        metadatas = [meta for _, _, meta in items]
        self._collection.upsert(ids=ids, embeddings=embeddings, metadatas=metadatas)

    async def query(self, vector: List[float], *, top_k: int = 5) -> List[Dict[str, Any]]:
        res = self._collection.query(query_embeddings=[vector], n_results=top_k)
        results: List[Dict[str, Any]] = []
        ids = (res.get("ids") or [[]])[0]
        metadatas = (res.get("metadatas") or [[]])[0]
        distances = (res.get("distances") or [[]])[0]
        for _id, meta, dist in zip(ids, metadatas, distances):
            results.append(
                {
                    "id": _id,
                    "score": float(dist),
                    "metadata": meta or {},
                }
            )
        return results


__all__ = ["ChromaVectorStore"]

