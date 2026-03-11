"""
API Key Management.

Provides API key generation, validation, and management.
"""

import hashlib
import secrets
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Optional

from fastapi import Depends, HTTPException, Request, Security
from fastapi.security import APIKeyHeader, APIKeyQuery


@dataclass
class APIKey:
    """
    API Key representation.

    Attributes:
        id: Unique key identifier.
        key_hash: Hashed key value (never store plain key).
        name: Human-readable name.
        scopes: Allowed scopes/permissions.
        created_at: Creation timestamp.
        expires_at: Expiration timestamp.
        last_used_at: Last usage timestamp.
        is_active: Whether key is active.
        rate_limit: Requests per minute limit.
        metadata: Additional metadata.
    """

    id: str
    key_hash: str
    name: str
    scopes: list[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None
    last_used_at: Optional[datetime] = None
    is_active: bool = True
    rate_limit: Optional[int] = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def is_expired(self) -> bool:
        """Check if key is expired."""
        if self.expires_at is None:
            return False
        return datetime.utcnow() > self.expires_at

    def has_scope(self, scope: str) -> bool:
        """Check if key has a specific scope."""
        if "*" in self.scopes:
            return True
        return scope in self.scopes

    def has_all_scopes(self, scopes: list[str]) -> bool:
        """Check if key has all specified scopes."""
        return all(self.has_scope(s) for s in scopes)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary (excludes key_hash for security)."""
        return {
            "id": self.id,
            "name": self.name,
            "scopes": self.scopes,
            "created_at": self.created_at.isoformat(),
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "last_used_at": self.last_used_at.isoformat() if self.last_used_at else None,
            "is_active": self.is_active,
            "rate_limit": self.rate_limit,
            "metadata": self.metadata,
        }


class APIKeyStore:
    """Base class for API key storage."""

    async def store(self, api_key: APIKey) -> None:
        """Store an API key."""
        pass

    async def get_by_hash(self, key_hash: str) -> Optional[APIKey]:
        """Get API key by hash."""
        pass

    async def get_by_id(self, key_id: str) -> Optional[APIKey]:
        """Get API key by ID."""
        pass

    async def update(self, api_key: APIKey) -> None:
        """Update API key."""
        pass

    async def delete(self, key_id: str) -> None:
        """Delete API key."""
        pass

    async def list_all(self) -> list[APIKey]:
        """List all API keys."""
        return []


class InMemoryAPIKeyStore(APIKeyStore):
    """In-memory API key store (for development/testing)."""

    def __init__(self):
        self._keys: dict[str, APIKey] = {}
        self._hash_to_id: dict[str, str] = {}

    async def store(self, api_key: APIKey) -> None:
        self._keys[api_key.id] = api_key
        self._hash_to_id[api_key.key_hash] = api_key.id

    async def get_by_hash(self, key_hash: str) -> Optional[APIKey]:
        key_id = self._hash_to_id.get(key_hash)
        if key_id:
            return self._keys.get(key_id)
        return None

    async def get_by_id(self, key_id: str) -> Optional[APIKey]:
        return self._keys.get(key_id)

    async def update(self, api_key: APIKey) -> None:
        self._keys[api_key.id] = api_key

    async def delete(self, key_id: str) -> None:
        if key_id in self._keys:
            key = self._keys[key_id]
            del self._hash_to_id[key.key_hash]
            del self._keys[key_id]

    async def list_all(self) -> list[APIKey]:
        return list(self._keys.values())


class APIKeyManager:
    """
    API Key manager for creating and validating API keys.

    Usage:
        manager = APIKeyManager()

        # Create a new key
        key, plain_key = await manager.create(
            name="my-service",
            scopes=["read", "write"],
            expires_in_days=365,
        )
        # Store plain_key securely - it cannot be retrieved later!

        # Validate a key
        api_key = await manager.validate("sk_live_xxxx")
        if api_key:
            print(f"Valid key: {api_key.name}")
    """

    KEY_PREFIX = "sk_live_"
    KEY_LENGTH = 32

    def __init__(
        self,
        store: Optional[APIKeyStore] = None,
        prefix: str = "sk_live_",
    ):
        """
        Initialize API key manager.

        Args:
            store: API key store implementation.
            prefix: Prefix for generated keys.
        """
        self._store = store or InMemoryAPIKeyStore()
        self._prefix = prefix

    def _generate_key(self) -> str:
        """Generate a new API key."""
        return f"{self._prefix}{secrets.token_urlsafe(self.KEY_LENGTH)}"

    def _hash_key(self, key: str) -> str:
        """Hash an API key for storage."""
        return hashlib.sha256(key.encode()).hexdigest()

    async def create(
        self,
        name: str,
        scopes: Optional[list[str]] = None,
        expires_in_days: Optional[int] = None,
        rate_limit: Optional[int] = None,
        metadata: Optional[dict[str, Any]] = None,
    ) -> tuple[APIKey, str]:
        """
        Create a new API key.

        Args:
            name: Human-readable name for the key.
            scopes: List of allowed scopes.
            expires_in_days: Days until expiration (None = no expiration).
            rate_limit: Requests per minute limit.
            metadata: Additional metadata.

        Returns:
            Tuple of (APIKey object, plain text key).
            The plain text key should be given to the user once and not stored.
        """
        import uuid

        plain_key = self._generate_key()
        key_hash = self._hash_key(plain_key)

        expires_at = None
        if expires_in_days:
            expires_at = datetime.utcnow() + timedelta(days=expires_in_days)

        api_key = APIKey(
            id=str(uuid.uuid4()),
            key_hash=key_hash,
            name=name,
            scopes=scopes or ["*"],
            expires_at=expires_at,
            rate_limit=rate_limit,
            metadata=metadata or {},
        )

        await self._store.store(api_key)
        return api_key, plain_key

    async def validate(self, plain_key: str) -> Optional[APIKey]:
        """
        Validate an API key.

        Args:
            plain_key: Plain text API key.

        Returns:
            APIKey if valid, None otherwise.
        """
        key_hash = self._hash_key(plain_key)
        api_key = await self._store.get_by_hash(key_hash)

        if api_key is None:
            return None

        if not api_key.is_active:
            return None

        if api_key.is_expired():
            return None

        # Update last used
        api_key.last_used_at = datetime.utcnow()
        await self._store.update(api_key)

        return api_key

    async def revoke(self, key_id: str) -> bool:
        """
        Revoke an API key.

        Args:
            key_id: Key ID to revoke.

        Returns:
            True if revoked, False if not found.
        """
        api_key = await self._store.get_by_id(key_id)
        if api_key:
            api_key.is_active = False
            await self._store.update(api_key)
            return True
        return False

    async def rotate(self, key_id: str) -> Optional[tuple[APIKey, str]]:
        """
        Rotate an API key (generate new key, invalidate old).

        Args:
            key_id: Key ID to rotate.

        Returns:
            Tuple of (new APIKey, new plain key) or None if not found.
        """
        old_key = await self._store.get_by_id(key_id)
        if old_key is None:
            return None

        # Create new key with same properties
        new_key, plain_key = await self.create(
            name=old_key.name,
            scopes=old_key.scopes,
            rate_limit=old_key.rate_limit,
            metadata=old_key.metadata,
        )

        # Revoke old key
        await self.revoke(key_id)

        return new_key, plain_key

    async def list_keys(self) -> list[APIKey]:
        """List all API keys."""
        return await self._store.list_all()


class APIKeyValidator:
    """
    FastAPI dependency for API key validation.

    Usage:
        from fastapi import Depends

        validator = APIKeyValidator(manager)

        @app.get("/protected")
        async def protected(api_key: APIKey = Depends(validator)):
            return {"key": api_key.name}
    """

    def __init__(
        self,
        manager: APIKeyManager,
        header_name: str = "X-API-Key",
        query_name: str = "api_key",
        required_scopes: Optional[list[str]] = None,
    ):
        """
        Initialize validator.

        Args:
            manager: API key manager.
            header_name: Header name for API key.
            query_name: Query parameter name for API key.
            required_scopes: Required scopes for access.
        """
        self._manager = manager
        self._header_scheme = APIKeyHeader(name=header_name, auto_error=False)
        self._query_scheme = APIKeyQuery(name=query_name, auto_error=False)
        self._required_scopes = required_scopes or []

    async def __call__(self, request: Request) -> APIKey:
        """Validate API key from request."""
        # Try header first, then query
        key = request.headers.get("X-API-Key") or request.query_params.get("api_key")

        if not key:
            raise HTTPException(
                status_code=401,
                detail="API key required",
                headers={"WWW-Authenticate": "ApiKey"},
            )

        api_key = await self._manager.validate(key)
        if api_key is None:
            raise HTTPException(
                status_code=401,
                detail="Invalid or expired API key",
            )

        # Check scopes
        if self._required_scopes and not api_key.has_all_scopes(self._required_scopes):
            raise HTTPException(
                status_code=403,
                detail=f"Missing required scopes: {self._required_scopes}",
            )

        return api_key


def require_api_key(
    manager: APIKeyManager,
    scopes: Optional[list[str]] = None,
) -> APIKeyValidator:
    """
    Create an API key validator dependency.

    Usage:
        @app.get("/protected", dependencies=[Depends(require_api_key(manager))])
        async def protected():
            pass

        @app.get("/admin", dependencies=[Depends(require_api_key(manager, scopes=["admin"]))])
        async def admin():
            pass
    """
    return APIKeyValidator(manager, required_scopes=scopes)
