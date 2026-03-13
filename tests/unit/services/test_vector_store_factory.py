"""
Tests for the vector store factory in services.vectors.client.
"""

from types import SimpleNamespace


def test_build_vector_store_returns_none_when_all_disabled(monkeypatch):
    """
    When no vector store backend is enabled, build_vector_store should return None.
    """

    from services.vectors import client

    # Fake configuration object matching VectorsConfigurationDTO shape
    fake_cfg = SimpleNamespace(
        pinecone=SimpleNamespace(enabled=False, api_key=None, environment=None, index_name=""),
        qdrant=SimpleNamespace(enabled=False, url="", api_key=None, collection_name=""),
        weaviate=SimpleNamespace(enabled=False, url="", api_key=None, class_name=""),
        pgvector=SimpleNamespace(
            enabled=False,
            dsn="",
            table="",
            vector_column="",
            id_column="",
            metadata_column="",
        ),
        faiss=SimpleNamespace(enabled=False, use_gpu=False),
        chroma=SimpleNamespace(enabled=False, persist_directory=""),
    )

    class DummyVectorsConfiguration:
        @classmethod
        def instance(cls):
            return cls()

        def get_config(self):
            return fake_cfg

    # Patch the configuration used by the factory
    monkeypatch.setattr(client, "VectorsConfiguration", DummyVectorsConfiguration)

    store = client.build_vector_store()
    assert store is None

