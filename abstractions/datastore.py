"""Datastore Abstractions Module.

Interfaces are defined in ``fast_datastores.interfaces`` and re-exported here so
existing ``from abstractions.datastore import …`` imports keep working.
"""

from fast_datastores.interfaces import (
    IDataStore,
    IDocumentStore,
    IKeyValueStore,
    IRelationalDataI,
    ISearchStore,
    IWideColumnStore,
)

__all__ = [
    "IDataStore",
    "IDocumentStore",
    "IKeyValueStore",
    "IRelationalDataI",
    "ISearchStore",
    "IWideColumnStore",
]
