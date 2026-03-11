from typing import Final


class FilterOperator:
    """
    Enumeration of filter operators for flexible querying.

    Provides constants for common SQL comparison operators
    that can be used with retrieve_record_by_filter.

    Example:
        >>> filters = [
        ...     ("age", FilterOperator.GTE, 18),
        ...     ("status", FilterOperator.IN, ["active", "pending"]),
        ... ]
    """

    EQ: Final[str] = "eq"           # Equal (default)
    NE: Final[str] = "ne"           # Not equal
    LT: Final[str] = "lt"           # Less than
    LE: Final[str] = "le"           # Less than or equal
    GT: Final[str] = "gt"           # Greater than
    GE: Final[str] = "ge"           # Greater than or equal
    GTE: Final[str] = "ge"          # Alias for GE
    LTE: Final[str] = "le"          # Alias for LE
    IN: Final[str] = "in"           # In list
    NOT_IN: Final[str] = "not_in"   # Not in list
    LIKE: Final[str] = "like"       # SQL LIKE (use % for wildcards)
    ILIKE: Final[str] = "ilike"     # Case-insensitive LIKE
    IS_NULL: Final[str] = "is_null" # IS NULL
    IS_NOT_NULL: Final[str] = "is_not_null"  # IS NOT NULL
    BETWEEN: Final[str] = "between" # Between two values
