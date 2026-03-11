"""
Vector store abstraction.

Supports Pinecone, Qdrant, Weaviate, and PGVector via a minimal
``IVectorStore`` interface.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Tuple

from loguru import logger

from configurations.vectors import VectorsConfiguration

try:  # Optional deps
    import pinecone  # type: ignore[import]
except Exception:  # pragma: no cover - optional
    pinecone = None  # type: ignore[assignment]

try:
    from qdrant_client import QdrantClient, models as qdrant_models
except Exception:  # pragma: no cover - optional
    QdrantClient = None  # type: ignore[assignment]
    qdrant_models = None  # type: ignore[assignment]

try:
    import weaviate  # type: ignore[import]
except Exception:  # pragma: no cover - optional
    weaviate = None  # type: ignore[assignment]

try:
    import psycopg2
except Exception:  # pragma: no cover - optional
    psycopg2 = None  # type: ignore[assignment]


class IVectorStore(ABC):
    """
    Minimal vector store interface.
    """

    @abstractmethod
    async def upsert(self, items: List[Tuple[str, List[float], Dict[str, Any]]]) -> None:  # pragma: no cover - interface
        """
        Upsert a list of (id, vector, metadata) items.
        """

    @abstractmethod
    async def query(self, vector: List[float], *, top_k: int = 5) -> List[Dict[str, Any]]:  # pragma: no cover - interface
        """
        Query similar vectors and return metadata with scores.
        """


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


class QdrantVectorStore(IVectorStore):
    def __init__(self, url: str, api_key: Optional[str], collection_name: str) -> None:
        if QdrantClient is None or qdrant_models is None:  # pragma: no cover - optional
            raise RuntimeError("qdrant-client is not installed")
        self._client = QdrantClient(url=url, api_key=api_key or None)
        self._collection = collection_name

    async def upsert(self, items: List[Tuple[str, List[float], Dict[str, Any]]]) -> None:
        points = [
            qdrant_models.PointStruct(
                id=_id,
                vector=vec,
                payload=meta,
            )
            for _id, vec, meta in items
        ]
        self._client.upsert(collection_name=self._collection, points=points)

    async def query(self, vector: List[float], *, top_k: int = 5) -> List[Dict[str, Any]]:
        res = self._client.search(
            collection_name=self._collection,
            query_vector=vector,
            limit=top_k,
        )
        out: List[Dict[str, Any]] = []
        for pt in res or []:
            out.append(
                {
                    "id": str(pt.id),
                    "score": pt.score,
                    "metadata": pt.payload or {},
                }
            )
        return out


class WeaviateVectorStore(IVectorStore):
    def __init__(self, url: str, api_key: Optional[str], class_name: str) -> None:
        if weaviate is None:  # pragma: no cover - optional
            raise RuntimeError("weaviate-client is not installed")
        auth_config = None
        if api_key:
            from weaviate.auth import AuthApiKey

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


class PGVectorStore(IVectorStore):
    def __init__(
        self,
        dsn: str,
        table: str,
        vector_column: str,
        id_column: str,
        metadata_column: str,
    ) -> None:
        if psycopg2 is None:  # pragma: no cover - optional
            raise RuntimeError("psycopg2 is not installed")
        self._dsn = dsn
        self._table = table
        self._vector_column = vector_column
        self._id_column = id_column
        self._metadata_column = metadata_column

    def _connect(self):
        return psycopg2.connect(self._dsn)

    async def upsert(self, items: List[Tuple[str, List[float], Dict[str, Any]]]) -> None:
        import json

        with self._connect() as conn:
            with conn.cursor() as cur:
                for _id, vec, meta in items:
                    cur.execute(
                        f"""
                        INSERT INTO {self._table} ({self._id_column}, {self._vector_column}, {self._metadata_column})
                        VALUES (%s, %s, %s)
                        ON CONFLICT ({self._id_column})
                        DO UPDATE SET
                            {self._vector_column} = EXCLUDED.{self._vector_column},
                            {self._metadata_column} = EXCLUDED.{self._metadata_column}
                        """,
                        (_id, vec, json.dumps(meta)),
                    )

    async def query(self, vector: List[float], *, top_k: int = 5) -> List[Dict[str, Any]]:
        import json

        with self._connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    f"""
                    SELECT {self._id_column}, {self._metadata_column},
                           1 - ({self._vector_column} <=> %s) AS score
                    FROM {self._table}
                    ORDER BY {self._vector_column} <=> %s
                    LIMIT %s
                    """,
                    (vector, vector, top_k),
                )
                rows = cur.fetchall()
        out: List[Dict[str, Any]] = []
        for _id, meta_json, score in rows:
            out.append(
                {
                    "id": str(_id),
                    "score": float(score),
                    "metadata": json.loads(meta_json or "{}"),
                }
            )
        return out


def build_vector_store() -> Optional[IVectorStore]:
    """
    Build a vector store instance from configuration.

    Priority:
      - Pinecone
      - Qdrant
      - Weaviate
      - PGVector
    """

    cfg = VectorsConfiguration.instance().get_config()

    if cfg.pinecone.enabled and cfg.pinecone.api_key:
        try:
            return PineconeVectorStore(
                api_key=cfg.pinecone.api_key,
                environment=cfg.pinecone.environment,
                index_name=cfg.pinecone.index_name,
            )
        except Exception as exc:  # pragma: no cover - defensive
            logger.warning("Failed to initialize Pinecone vector store: %s", exc)

    if cfg.qdrant.enabled:
        try:
            return QdrantVectorStore(
                url=cfg.qdrant.url,
                api_key=cfg.qdrant.api_key,
                collection_name=cfg.qdrant.collection_name,
            )
        except Exception as exc:  # pragma: no cover - defensive
            logger.warning("Failed to initialize Qdrant vector store: %s", exc)

    if cfg.weaviate.enabled:
        try:
            return WeaviateVectorStore(
                url=cfg.weaviate.url,
                api_key=cfg.weaviate.api_key,
                class_name=cfg.weaviate.class_name,
            )
        except Exception as exc:  # pragma: no cover - defensive
            logger.warning("Failed to initialize Weaviate vector store: %s", exc)

    if cfg.pgvector.enabled:
        try:
            return PGVectorStore(
                dsn=cfg.pgvector.dsn,
                table=cfg.pgvector.table,
                vector_column=cfg.pgvector.vector_column,
                id_column=cfg.pgvector.id_column,
                metadata_column=cfg.pgvector.metadata_column,
            )
        except Exception as exc:  # pragma: no cover - defensive
            logger.warning("Failed to initialize PGVector store: %s", exc)

    logger.info("No vector store is enabled.")
    return None


__all__ = [
    "IVectorStore",
    "PineconeVectorStore",
    "QdrantVectorStore",
    "WeaviateVectorStore",
    "PGVectorStore",
    "build_vector_store",
]

