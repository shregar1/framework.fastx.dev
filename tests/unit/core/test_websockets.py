"""
Tests for basic WebSocket support provided by core.websockets.router.
"""

from fastapi.testclient import TestClient

from app import app
from start_utils import unprotected_routes


class TestWebSockets:
    @classmethod
    def setup_class(cls):
        # Mark websocket paths as unprotected for auth middleware
        unprotected_routes.update(
            {
                "/ws/echo",
                "/ws/rooms/test-room",
            }
        )
        cls.client = TestClient(app)

    def test_echo_websocket(self):
        with self.client.websocket_connect("/ws/echo") as websocket:
            websocket.send_text("hello")
            data = websocket.receive_text()
            assert data == "hello"

