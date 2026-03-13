from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

from core.utils.optional_imports import optional_import

weaviate, AuthApiKey = optional_import("weaviate", "auth.AuthApiKey")

from .abstraction import IVectorStore


class WeaviateVectorStore(IVectorStore):
    def __init__(self, url: str, api_key: Optional[str], class_name: str) -> None:
        if weaviate is None:  # pragma: no cover - optional
            raise RuntimeError("weaviate-client is not installed")
        auth_config = None
        if api_key and AuthApiKey is not None:
            auth_config = AuthApiKey(api_key=api_key)
        self._client = weaviate.Client(url=url, auth_client_secret=auth_config)
        self._class = class_name

    async def upsert(self, items: List[Tuple[str, List[float], Dict[str, Any]]]) -> None:
        with self._client.batch as batch:
            for _id, vec, meta in items:
                batch.add_data_object(
                    data_object=meta,
                    class_name=self._class,
                    uuid=_id,
                    vector=vec,
                )

    async def query(self, vector: List[float], *, top_k: int = 5) -> List[Dict[str, Any]]:
        res = (
            self._client.query.get(self._class, ["uuid", "metadata"])
            .with_near_vector({"vector": vector})
            .with_limit(top_k)
            .do()
        )
        out: List[Dict[str, Any]] = []
        results = res.get("data", {}).get("Get", {}).get(self._class, [])
        for item in results:
            out.append(
                {
                    "id": item.get("uuid"),
                    "score": None,
                    "metadata": item.get("metadata", {}),
                }
            )
        return out


__all__ = ["WeaviateVectorStore"]

