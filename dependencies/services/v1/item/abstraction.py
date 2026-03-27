"""v1 item service dependency abstraction."""

from dependencies.services.v1.abstraction import IV1ServiceDependency


class IItemServiceDependency(IV1ServiceDependency):
    """Interface for v1 item-scoped service dependencies."""
