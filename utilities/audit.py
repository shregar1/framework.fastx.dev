"""Audit trail helper.

Provides :func:`log_audit` for recording security-relevant events
(login, logout, password reset, etc.) into the audit log table.
"""

from __future__ import annotations

from typing import Any, Optional

from start_utils import logger


def log_audit(
    session: Any,
    action: str,
    resource_type: str,
    *,
    actor_id: Any = None,
    actor_urn: Optional[str] = None,
    resource_id: Optional[str] = None,
    metadata: Optional[dict[str, Any]] = None,
    ip: Optional[str] = None,
) -> None:
    """Record an audit event.

    When the ``AuditLog`` model is available the event is persisted;
    otherwise it is emitted as a structured log line so nothing is lost.

    Args:
        session: SQLAlchemy session (used for DB persistence).
        action: Dot-separated action name (e.g. ``login.success``).
        resource_type: Type of resource affected (e.g. ``user``).
        actor_id: ID of the acting user.
        actor_urn: URN of the acting user.
        resource_id: ID of the affected resource.
        metadata: Extra context dictionary.
        ip: Client IP address.
    """
    try:
        from fast_database.persistence.models.audit_log import AuditLog  # noqa: F401

        record = AuditLog(
            action=action,
            resource_type=resource_type,
            actor_id=actor_id,
            actor_urn=actor_urn,
            resource_id=resource_id,
            metadata_=metadata or {},
            ip_address=ip,
        )
        session.add(record)
        session.flush()
    except Exception:
        # Audit failures are intentionally non-fatal — a broken audit write
        # must not crash the request. We still want visibility, so log at
        # error level with the full traceback instead of swallowing silently.
        logger.bind(
            action=action,
            resource_type=resource_type,
            actor_id=actor_id,
            resource_id=resource_id,
            ip=ip,
        ).error("audit.%s failed to persist", action)
        logger.exception("log_audit: failed to record audit event %s", action)


__all__ = ["log_audit"]
