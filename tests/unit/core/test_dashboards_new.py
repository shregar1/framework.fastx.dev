"""
Tests for new FastMVC dashboards: queues, tenants, and secrets.
"""

from fastapi.testclient import TestClient

from app import app
from start_utils import unprotected_routes


class TestNewDashboards:
    """Smoke tests to ensure new dashboards are wired and respond."""

    @classmethod
    def setup_class(cls):
        # Mark dashboard routes as unprotected so auth middleware doesn't block them.
        unprotected_routes.update(
            {
                "/dashboard/queues",
                "/dashboard/queues/state",
                "/dashboard/tenants",
                "/dashboard/tenants/state",
                "/dashboard/secrets",
                "/dashboard/secrets/state",
            }
        )
        cls.client = TestClient(app)

    def test_queues_dashboard_html(self):
        response = self.client.get("/dashboard/queues")
        assert response.status_code == 200
        assert "<title>FastMVC Queues & Jobs Dashboard</title>" in response.text

    def test_queues_dashboard_state(self):
        response = self.client.get("/dashboard/queues/state")
        assert response.status_code == 200
        data = response.json()
        assert "queues" in data
        assert "jobs" in data

    def test_tenants_dashboard_html(self):
        response = self.client.get("/dashboard/tenants")
        assert response.status_code == 200
        assert "<title>FastMVC Tenants & Auth Dashboard</title>" in response.text

    def test_tenants_dashboard_state(self):
        response = self.client.get("/dashboard/tenants/state")
        assert response.status_code == 200
        data = response.json()
        assert "tenants" in data
        assert "flags" in data
        assert "idps" in data

    def test_secrets_dashboard_html(self):
        response = self.client.get("/dashboard/secrets")
        assert response.status_code == 200
        assert "<title>FastMVC Secrets & Config Dashboard</title>" in response.text

    def test_secrets_dashboard_state(self):
        response = self.client.get("/dashboard/secrets/state")
        assert response.status_code == 200
        data = response.json()
        assert "backends" in data
        assert "health" in data
        assert "envDiff" in data

