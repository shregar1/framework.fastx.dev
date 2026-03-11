"""
Testing Utilities Module.

Provides testing helpers for FastMVC applications:
- Factory pattern for creating test data
- Mock helpers for external services
- Test fixtures
- Database test utilities

Usage:
    from core.testing import Factory, mock_external

    @Factory.define
    class UserFactory:
        email = Factory.faker("email")
        name = Factory.faker("name")

    user = await UserFactory.create()
    users = await UserFactory.create_batch(10)

    @mock_external("stripe.create_charge", return_value={"id": "ch_123"})
    async def test_payment():
        pass
"""

from core.testing.factories import Factory, FactoryField
from core.testing.mocks import MockExternalService, mock_external
from core.testing.fixtures import DatabaseTestCase, TestClient

__all__ = [
    "Factory",
    "FactoryField",
    "mock_external",
    "MockExternalService",
    "DatabaseTestCase",
    "TestClient",
]
