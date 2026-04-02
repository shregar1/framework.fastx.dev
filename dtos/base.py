"""Pydantic base model for DTOs with optional sanitization and security checks.

Provides :class:`ApplicationBaseModel` (Pydantic v2); use
:class:`~dtos.config.DtoConfigBuilder` to merge defaults with any
:class:`~pydantic.ConfigDict` options
(``title``, ``str_strip_whitespace``, ``populate_by_name``, ``frozen``, …).

Serialization ``include`` / ``exclude`` are not global model settings in Pydantic v2;
pass them to :meth:`~pydantic.BaseModel.model_dump` / :meth:`~pydantic.BaseModel.model_dump_json`.

Subclass :class:`ApplicationBaseModel`, call :meth:`~dtos.config.DtoConfigBuilder.build_config`
with extra keys, or add ``model_validator`` / ``computed_field`` / ``Field`` for richer schemas.

Usage:
    >>> from dtos.base import ApplicationBaseModel
    >>> from dtos.config import DtoConfigBuilder
    >>>
    >>> class MyRequestDTO(ApplicationBaseModel):
    ...     name: str
    >>>
    >>> class StrictDTO(ApplicationBaseModel):
    ...     model_config = DtoConfigBuilder.build_config(
    ...         title="StrictDTO", str_strip_whitespace=True
    ...     )
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from loguru import logger
from pydantic import BaseModel, field_validator

# Optional fast_utilities (requires fastx-mvc[platform])
try:
    from fast_utilities.validation import (  # pyright: ignore[reportMissingImports]
        SecurityValidators,
        ValidationUtility,
    )
except ImportError:
    SecurityValidators = None  # type: ignore
    ValidationUtility = None  # type: ignore

from dtos.config import DtoConfigBuilder

__all__ = ["ApplicationBaseModel"]


class ApplicationBaseModel(BaseModel):
    """Pydantic v2 base for DTOs: optional string sanitization, security scan, strict defaults.

    Subclasses may set ``model_config = DtoConfigBuilder.build_config(...)`` to add options
    without re-specifying defaults.
    """

    model_config = DtoConfigBuilder.build_config()

    @field_validator("*", mode="before")
    @classmethod
    def sanitize_strings(cls, v: Any) -> Any:
        """Trim and normalize string inputs before field validation."""
        if ValidationUtility:
            logger.debug("Sanitizing string inputs in {}", cls.__qualname__)
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

        logger.debug("Performing security validation on {}", self.__class__.__qualname__)
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
