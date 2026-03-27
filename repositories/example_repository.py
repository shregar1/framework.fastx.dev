"""Example Repository."""

from typing import Any, Dict, List, Optional
from repositories.abstraction import IRepository


class ExampleRepository(IRepository):
    """Stub repository for demonstration.
    Does not use an actual dataI.
    """

    def __init__(self, **kwargs: Any):
        """Execute __init__ operation."""
        super().__init__(**kwargs)
        # In-memory storage for stubbing
        # Simulating storage as a class attribute to persist across requests in dev mode
        if not hasattr(self.__class__, "_items"):
            self.__class__._items = [
                {
                    "id": "ex-1",
                    "name": "Initial Item",
                    "description": "Stub data",
                    "status": "active",
                },
            ]

    @property
    def items(self) -> List[Dict[str, Any]]:
        """Get the in-memory items."""
        return self.__class__._items

    def create_record(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Stub create operation."""
        new_item = {"id": f"ex-{len(self.items) + 1}", **data}
        self.items.append(new_item)
        return new_item

    def retrieve_record_by_id(self, id: Any) -> Optional[Dict[str, Any]]:
        """Stub retrieve operation."""
        for item in self.items:
            if item["id"] == id:
                return item
        return None

    def list_all(self) -> List[Dict[str, Any]]:
        """Stub list operation."""
        return self.items
