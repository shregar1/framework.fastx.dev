"""Enhanced Base Model Module.

Provides :class:`EnhancedBaseModel` (Pydantic v2) plus :func:`enhanced_config` so
subclasses can extend defaults with any :class:`~pydantic.ConfigDict` options
(``title``, ``str_strip_whitespace``, ``populate_by_name``, ``frozen``, …).

Serialization ``include`` / ``exclude`` are not global model settings in Pydantic v2;
pass them to :meth:`~pydantic.BaseModel.model_dump` / :meth:`~pydantic.BaseModel.model_dump_json`.

Subclass :class:`EnhancedBaseModel`, call :func:`enhanced_config` with extra keys, or add
``model_validator`` / ``computed_field`` / ``Field`` for richer schemas.

Usage:
    >>> from dtos.base import EnhancedBaseModel, enhanced_config
    >>>
    >>> class MyRequestDTO(EnhancedBaseModel):
    ...     name: str
    >>>
    >>> class StrictDTO(EnhancedBaseModel):
    ...     model_config = enhanced_config(title="StrictDTO", str_strip_whitespace=True)
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from loguru import logger
from pydantic import BaseModel, ConfigDict, field_validator

# Optional fast_utilities (requires pyfastmvc[platform])
try:
    from fast_utilities.validation import SecurityValidators, ValidationUtility
except ImportError:
    SecurityValidators = None  # type: ignore
    ValidationUtility = None  # type: ignore

__all__ = ["EnhancedBaseModel", "enhanced_config"]

_ENHANCED_DEFAULTS: dict[str, Any] = {
    "extra": "forbid",
    "validate_assignment": True,
    "use_enum_values": True,
}


def enhanced_config(**overrides: Any) -> ConfigDict:
    """Build a :class:`~pydantic.ConfigDict` by merging *overrides* into the
    defaults used by :class:`EnhancedBaseModel`.

    Common overrides: ``title``, ``str_strip_whitespace``, ``populate_by_name``,
    ``frozen``, ``validate_default``, ``json_schema_extra``, etc.
    """
    merged = {**_ENHANCED_DEFAULTS, **overrides}
    return ConfigDict(**merged)


class EnhancedBaseModel(BaseModel):
    """Pydantic v2 base for request DTOs: sanitization, security checks, strict extras.

    Subclasses may set ``model_config = enhanced_config(...)`` to add options
    without re-specifying defaults.
    """

    model_config = enhanced_config()

    @field_validator("*", mode="before")
    @classmethod
    def sanitize_strings(cls, v: Any) -> Any:
        """Trim and normalize string inputs before field validation."""
        if ValidationUtility:
            logger.debug("Sanitizing string inputs in EnhancedBaseModel")
            if isinstance(v, str):
                return ValidationUtility.sanitize_string(v)
        return v

    def validate_security(self) -> dict[str, Any]:
        """Scan string fields for SQL injection, XSS, and path traversal patterns.

        Returns:
            ``{"is_valid": bool, "issues": list[str]}``

        """
        if not SecurityValidators:
            return {"is_valid": True, "issues": []}

        logger.debug("Performing security validation on EnhancedBaseModel")
        issues: list[str] = []

        for field_name, field_value in self.model_dump().items():
            if isinstance(field_value, str):
                if not SecurityValidators.validate_sql_injection_prevention(
                    field_value
                ):
                    issues.append(f"Potential SQL injection in field '{field_name}'")

                if not SecurityValidators.validate_xss_prevention(field_value):
                    issues.append(f"Potential XSS in field '{field_name}'")

                if not SecurityValidators.validate_path_traversal_prevention(
                    field_value
                ):
                    issues.append(f"Potential path traversal in field '{field_name}'")

        return {"is_valid": len(issues) == 0, "issues": issues}
