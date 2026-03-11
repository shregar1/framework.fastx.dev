"""
Audit Logging Module.

Provides audit logging for tracking user actions and data changes
for compliance and security purposes.
"""

import functools
import hashlib
import json
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Optional

from loguru import logger


class AuditAction(str, Enum):
    """Standard audit actions."""

    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"
    LOGIN = "login"
    LOGOUT = "logout"
    PERMISSION_CHANGE = "permission_change"
    EXPORT = "export"
    IMPORT = "import"


@dataclass
class AuditEntry:
    """
    Audit log entry.

    Contains all information about an audited action.
    """

    id: str
    timestamp: datetime
    action: str
    resource_type: str
    resource_id: Optional[str]
    user_id: Optional[str]
    user_email: Optional[str]
    ip_address: Optional[str]
    user_agent: Optional[str]
    request_id: Optional[str]
    tenant_id: Optional[str]
    success: bool
    error_message: Optional[str] = None
    before_state: Optional[dict[str, Any]] = None
    after_state: Optional[dict[str, Any]] = None
    changes: Optional[dict[str, Any]] = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "timestamp": self.timestamp.isoformat(),
            "action": self.action,
            "resource_type": self.resource_type,
            "resource_id": self.resource_id,
            "user_id": self.user_id,
            "user_email": self.user_email,
            "ip_address": self.ip_address,
            "user_agent": self.user_agent,
            "request_id": self.request_id,
            "tenant_id": self.tenant_id,
            "success": self.success,
            "error_message": self.error_message,
            "before_state": self.before_state,
            "after_state": self.after_state,
            "changes": self.changes,
            "metadata": self.metadata,
        }

    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict())


class AuditStore:
    """Base class for audit log storage."""

    async def store(self, entry: AuditEntry) -> None:
        """Store an audit entry."""
        pass

    async def query(
        self,
        user_id: Optional[str] = None,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        action: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 100,
    ) -> list[AuditEntry]:
        """Query audit entries."""
        return []


class LogAuditStore(AuditStore):
    """Store audit entries using structured logging."""

    def __init__(self, logger_name: str = "audit"):
        self._logger = logger.bind(audit=True, logger_name=logger_name)

    async def store(self, entry: AuditEntry) -> None:
        """Log audit entry."""
        self._logger.info(
            f"AUDIT: {entry.action} on {entry.resource_type}",
            **entry.to_dict(),
        )


class DatabaseAuditStore(AuditStore):
    """
    Store audit entries in database.

    Requires a table with appropriate schema.
    """

    def __init__(self, session_factory: Any, table_name: str = "audit_logs"):
        self._session_factory = session_factory
        self._table_name = table_name

    async def store(self, entry: AuditEntry) -> None:
        """Store audit entry in database."""
        # Implementation would insert into database
        pass


class AuditLog:
    """
    Audit logger for tracking user actions.

    Usage:
        audit = AuditLog(store=LogAuditStore())

        # Log an action
        await audit.log(
            action="user.update",
            resource_type="User",
            resource_id="123",
            user_id="456",
            before_state={"name": "Old Name"},
            after_state={"name": "New Name"},
        )
    """

    def __init__(self, store: Optional[AuditStore] = None):
        """
        Initialize audit logger.

        Args:
            store: AuditStore implementation for persistence.
        """
        self._store = store or LogAuditStore()

    def _generate_id(self) -> str:
        """Generate unique audit entry ID."""
        import uuid
        return str(uuid.uuid4())

    def _compute_diff(
        self,
        before: Optional[dict[str, Any]],
        after: Optional[dict[str, Any]],
    ) -> Optional[dict[str, Any]]:
        """Compute differences between states."""
        if not before or not after:
            return None

        changes = {}
        all_keys = set(before.keys()) | set(after.keys())

        for key in all_keys:
            before_val = before.get(key)
            after_val = after.get(key)
            if before_val != after_val:
                changes[key] = {
                    "before": before_val,
                    "after": after_val,
                }

        return changes if changes else None

    async def log(
        self,
        action: str,
        resource_type: str,
        resource_id: Optional[str] = None,
        user_id: Optional[str] = None,
        user_email: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        request_id: Optional[str] = None,
        tenant_id: Optional[str] = None,
        success: bool = True,
        error_message: Optional[str] = None,
        before_state: Optional[dict[str, Any]] = None,
        after_state: Optional[dict[str, Any]] = None,
        include_diff: bool = True,
        **metadata: Any,
    ) -> AuditEntry:
        """
        Log an audit entry.

        Args:
            action: Action performed (e.g., "user.update").
            resource_type: Type of resource (e.g., "User").
            resource_id: ID of the resource.
            user_id: ID of the user performing the action.
            user_email: Email of the user.
            ip_address: Client IP address.
            user_agent: Client user agent.
            request_id: Request correlation ID.
            tenant_id: Tenant ID for multi-tenant apps.
            success: Whether the action succeeded.
            error_message: Error message if failed.
            before_state: State before the action.
            after_state: State after the action.
            include_diff: Whether to compute and include diff.
            **metadata: Additional metadata.

        Returns:
            Created AuditEntry.
        """
        changes = None
        if include_diff and before_state and after_state:
            changes = self._compute_diff(before_state, after_state)

        entry = AuditEntry(
            id=self._generate_id(),
            timestamp=datetime.utcnow(),
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            user_id=user_id,
            user_email=user_email,
            ip_address=ip_address,
            user_agent=user_agent,
            request_id=request_id,
            tenant_id=tenant_id,
            success=success,
            error_message=error_message,
            before_state=before_state,
            after_state=after_state,
            changes=changes,
            metadata=metadata,
        )

        await self._store.store(entry)
        return entry


# Global audit log instance
_audit_log: Optional[AuditLog] = None


def get_audit_log() -> AuditLog:
    """Get global audit log instance."""
    global _audit_log
    if _audit_log is None:
        _audit_log = AuditLog()
    return _audit_log


def set_audit_log(audit_log: AuditLog) -> None:
    """Set global audit log instance."""
    global _audit_log
    _audit_log = audit_log


def audit_log(
    action: str,
    resource_type: Optional[str] = None,
    include_args: bool = False,
    include_result: bool = False,
    include_diff: bool = False,
) -> Callable:
    """
    Decorator to automatically audit function calls.

    Usage:
        @audit_log(action="user.update", include_diff=True)
        async def update_user(user_id: str, data: dict):
            pass
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
            audit = get_audit_log()
            res_type = resource_type or func.__name__

            metadata: dict[str, Any] = {}
            if include_args:
                metadata["args"] = str(args)
                metadata["kwargs"] = {k: str(v) for k, v in kwargs.items()}

            try:
                result = await func(*args, **kwargs)

                if include_result:
                    metadata["result"] = str(result)

                await audit.log(
                    action=action,
                    resource_type=res_type,
                    success=True,
                    **metadata,
                )
                return result
            except Exception as e:
                await audit.log(
                    action=action,
                    resource_type=res_type,
                    success=False,
                    error_message=str(e),
                    **metadata,
                )
                raise

        @functools.wraps(func)
        def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
            # For sync functions, we can't use await
            # Log would need to be async-compatible
            return func(*args, **kwargs)

        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper

    return decorator
