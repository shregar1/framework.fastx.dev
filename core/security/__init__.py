"""
Security Module.

Provides security features for production applications:
- API Key management
- Webhook signature verification
- Field-level encryption
- Request signing

Usage:
    from core.security import APIKeyManager, WebhookVerifier, FieldEncryption

    # API Keys
    api_keys = APIKeyManager()
    key = await api_keys.create(name="my-service", scopes=["read", "write"])

    # Webhook verification
    verifier = WebhookVerifier(secret="webhook_secret")
    if verifier.verify(payload, signature):
        process_webhook(payload)

    # Field encryption
    encryption = FieldEncryption(key="...")
    encrypted = encryption.encrypt("sensitive_data")
"""

from core.security.api_keys import APIKey, APIKeyManager, APIKeyValidator
from core.security.encryption import FieldEncryption
from core.security.webhooks import WebhookVerifier

__all__ = [
    "APIKeyManager",
    "APIKey",
    "APIKeyValidator",
    "WebhookVerifier",
    "FieldEncryption",
]
