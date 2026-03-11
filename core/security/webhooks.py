"""
Webhook Verification.

Provides signature verification for incoming webhooks
to ensure authenticity and prevent replay attacks.
"""

import functools
import hashlib
import hmac
import time
from dataclasses import dataclass
from typing import Any, Callable, Optional, Union

from fastapi import HTTPException, Request


@dataclass
class WebhookConfig:
    """
    Webhook verification configuration.

    Attributes:
        secret: Webhook secret key.
        signature_header: Header containing signature.
        timestamp_header: Header containing timestamp.
        tolerance_seconds: Max age of webhook in seconds.
        algorithm: HMAC algorithm to use.
    """

    secret: str
    signature_header: str = "X-Signature"
    timestamp_header: str = "X-Timestamp"
    tolerance_seconds: int = 300  # 5 minutes
    algorithm: str = "sha256"


class WebhookVerificationError(Exception):
    """Raised when webhook verification fails."""

    pass


class WebhookVerifier:
    """
    Webhook signature verifier.

    Supports HMAC-based signature verification with timestamp
    validation to prevent replay attacks.

    Usage:
        verifier = WebhookVerifier(secret="webhook_secret")

        # Verify manually
        if verifier.verify(payload, signature, timestamp):
            process_webhook(payload)

        # Or use as decorator
        @verifier.verified
        async def handle_webhook(payload: dict):
            pass
    """

    def __init__(
        self,
        secret: str,
        signature_header: str = "X-Signature",
        timestamp_header: str = "X-Timestamp",
        tolerance_seconds: int = 300,
        algorithm: str = "sha256",
    ):
        """
        Initialize webhook verifier.

        Args:
            secret: Webhook secret key.
            signature_header: Header containing signature.
            timestamp_header: Header containing timestamp.
            tolerance_seconds: Max age of webhook in seconds.
            algorithm: HMAC algorithm (sha256, sha512, etc.).
        """
        self._secret = secret.encode() if isinstance(secret, str) else secret
        self._signature_header = signature_header
        self._timestamp_header = timestamp_header
        self._tolerance = tolerance_seconds
        self._algorithm = algorithm

    def compute_signature(
        self,
        payload: Union[str, bytes],
        timestamp: Optional[str] = None,
    ) -> str:
        """
        Compute HMAC signature for payload.

        Args:
            payload: Request body.
            timestamp: Timestamp string (included in signature if provided).

        Returns:
            Hex-encoded signature.
        """
        if isinstance(payload, str):
            payload = payload.encode()

        # Include timestamp in signed payload if provided
        if timestamp:
            signed_payload = f"{timestamp}.{payload.decode()}".encode()
        else:
            signed_payload = payload

        signature = hmac.new(
            self._secret,
            signed_payload,
            getattr(hashlib, self._algorithm),
        ).hexdigest()

        return signature

    def verify(
        self,
        payload: Union[str, bytes],
        signature: str,
        timestamp: Optional[str] = None,
    ) -> bool:
        """
        Verify webhook signature.

        Args:
            payload: Request body.
            signature: Provided signature.
            timestamp: Provided timestamp.

        Returns:
            True if valid.

        Raises:
            WebhookVerificationError: If verification fails.
        """
        # Check timestamp if provided
        if timestamp:
            try:
                ts = int(timestamp)
                now = int(time.time())
                if abs(now - ts) > self._tolerance:
                    raise WebhookVerificationError(
                        f"Webhook timestamp too old (tolerance: {self._tolerance}s)"
                    )
            except ValueError:
                raise WebhookVerificationError("Invalid timestamp format")

        # Compute expected signature
        expected = self.compute_signature(payload, timestamp)

        # Remove prefix if present (e.g., "sha256=")
        if "=" in signature:
            signature = signature.split("=", 1)[1]

        # Constant-time comparison
        if not hmac.compare_digest(expected, signature):
            raise WebhookVerificationError("Invalid signature")

        return True

    async def verify_request(self, request: Request) -> bytes:
        """
        Verify webhook from FastAPI request.

        Args:
            request: FastAPI request object.

        Returns:
            Request body if valid.

        Raises:
            HTTPException: If verification fails.
        """
        # Get signature
        signature = request.headers.get(self._signature_header)
        if not signature:
            raise HTTPException(
                status_code=401,
                detail=f"Missing {self._signature_header} header",
            )

        # Get timestamp if configured
        timestamp = request.headers.get(self._timestamp_header)

        # Get body
        body = await request.body()

        try:
            self.verify(body, signature, timestamp)
            return body
        except WebhookVerificationError as e:
            raise HTTPException(status_code=401, detail=str(e))

    def verified(self, func: Callable) -> Callable:
        """
        Decorator to verify webhook requests.

        Usage:
            @verifier.verified
            async def handle_webhook(request: Request):
                pass
        """

        @functools.wraps(func)
        async def wrapper(request: Request, *args: Any, **kwargs: Any) -> Any:
            await self.verify_request(request)
            return await func(request, *args, **kwargs)

        return wrapper


class MultiSecretWebhookVerifier:
    """
    Webhook verifier that supports multiple secrets.

    Useful when rotating secrets or handling webhooks
    from multiple sources.
    """

    def __init__(
        self,
        secrets: list[str],
        signature_header: str = "X-Signature",
        timestamp_header: str = "X-Timestamp",
        tolerance_seconds: int = 300,
    ):
        """
        Initialize with multiple secrets.

        Args:
            secrets: List of valid secrets.
            signature_header: Header containing signature.
            timestamp_header: Header containing timestamp.
            tolerance_seconds: Max age of webhook.
        """
        self._verifiers = [
            WebhookVerifier(
                secret=s,
                signature_header=signature_header,
                timestamp_header=timestamp_header,
                tolerance_seconds=tolerance_seconds,
            )
            for s in secrets
        ]

    def verify(
        self,
        payload: Union[str, bytes],
        signature: str,
        timestamp: Optional[str] = None,
    ) -> bool:
        """
        Verify using any of the configured secrets.

        Returns True if any secret validates the signature.
        """
        for verifier in self._verifiers:
            try:
                if verifier.verify(payload, signature, timestamp):
                    return True
            except WebhookVerificationError:
                continue

        raise WebhookVerificationError("Invalid signature (no matching secret)")


# Common webhook configurations
STRIPE_WEBHOOK_CONFIG = WebhookConfig(
    secret="",  # Set from environment
    signature_header="Stripe-Signature",
    timestamp_header="",  # Stripe includes timestamp in signature header
    algorithm="sha256",
)

GITHUB_WEBHOOK_CONFIG = WebhookConfig(
    secret="",
    signature_header="X-Hub-Signature-256",
    algorithm="sha256",
)

SLACK_WEBHOOK_CONFIG = WebhookConfig(
    secret="",
    signature_header="X-Slack-Signature",
    timestamp_header="X-Slack-Request-Timestamp",
    algorithm="sha256",
)
