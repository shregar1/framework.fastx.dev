"""
Tests for FastMVC application.
"""



class TestAppConfiguration:
    """Tests for app configuration."""

    def test_app_exists(self):
        """Test app instance exists."""
        from app import app
        assert app is not None

    def test_app_has_title(self):
        """Test app has proper title."""
        from app import app
        assert app.title == "FastMVC API"

    def test_app_has_docs_url(self):
        """Test app has docs URL configured."""
        from app import app
        assert app.docs_url == "/docs"

    def test_app_has_redoc_url(self):
        """Test app has redoc URL configured."""
        from app import app
        assert app.redoc_url == "/redoc"


class TestMiddlewareStack:
    """Tests for middleware configuration."""

    def test_middleware_is_configured(self):
        """Test middleware stack is configured."""
        from app import app
        # App should have middleware
        assert len(app.user_middleware) > 0


class TestRouterConfiguration:
    """Tests for router configuration."""

    def test_user_router_included(self):
        """Test user router is included."""
        from app import app
        routes = [route.path for route in app.routes]

        # User routes should be included
        assert "/user/login" in routes or any("/user" in r for r in routes)


class TestEnvironmentVariables:
    """Tests for environment variable loading."""

    def test_rate_limit_variables_loaded(self):
        """Test rate limit environment variables are loaded."""
        from app import (
            RATE_LIMIT_BURST_LIMIT,
            RATE_LIMIT_REQUESTS_PER_HOUR,
            RATE_LIMIT_REQUESTS_PER_MINUTE,
        )
        assert isinstance(RATE_LIMIT_REQUESTS_PER_MINUTE, int)
        assert isinstance(RATE_LIMIT_REQUESTS_PER_HOUR, int)
        assert isinstance(RATE_LIMIT_BURST_LIMIT, int)
