"""FetchUser Repository."""

from typing import Any, Dict
from repositories.user.abstraction import IUserRepository


class FetchUserRepository(IUserRepository):
    """Represents the FetchUserRepository class."""

    def create_record(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute create_record operation.

        Args:
            data: The data parameter.

        Returns:
            The result of the operation.
        """
        return {"id": "1", **data}
