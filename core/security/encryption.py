"""
Field-Level Encryption.

Provides encryption for sensitive data fields in your models.
"""

import base64
import hashlib
import os
import secrets
from dataclasses import dataclass
from typing import Any, Generic, Optional, TypeVar, Union

from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

T = TypeVar("T")


@dataclass
class EncryptedValue:
    """Container for encrypted data."""

    ciphertext: str
    algorithm: str = "fernet"
    key_id: Optional[str] = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "ciphertext": self.ciphertext,
            "algorithm": self.algorithm,
            "key_id": self.key_id,
        }


class FieldEncryption:
    """
    Field-level encryption utility.

    Uses Fernet symmetric encryption for secure field encryption.

    Usage:
        encryption = FieldEncryption(key="your-secret-key")

        # Encrypt
        encrypted = encryption.encrypt("sensitive_data")

        # Decrypt
        decrypted = encryption.decrypt(encrypted)

        # With Pydantic models
        class User(BaseModel):
            email: str
            ssn: str  # Store encrypted

            @validator("ssn", pre=True)
            def encrypt_ssn(cls, v):
                return encryption.encrypt(v)
    """

    def __init__(
        self,
        key: Optional[str] = None,
        key_bytes: Optional[bytes] = None,
        salt: Optional[bytes] = None,
    ):
        """
        Initialize encryption with key.

        Args:
            key: String key (will be derived using PBKDF2).
            key_bytes: Pre-computed 32-byte key.
            salt: Salt for key derivation (generated if not provided).
        """
        if key_bytes:
            self._fernet = Fernet(base64.urlsafe_b64encode(key_bytes))
        elif key:
            salt = salt or os.urandom(16)
            self._salt = salt
            derived_key = self._derive_key(key, salt)
            self._fernet = Fernet(derived_key)
        else:
            # Generate a random key
            self._fernet = Fernet(Fernet.generate_key())

    @staticmethod
    def _derive_key(password: str, salt: bytes) -> bytes:
        """Derive encryption key from password using PBKDF2."""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend(),
        )
        return base64.urlsafe_b64encode(kdf.derive(password.encode()))

    @staticmethod
    def generate_key() -> str:
        """Generate a new encryption key."""
        return Fernet.generate_key().decode()

    def encrypt(self, plaintext: Union[str, bytes]) -> str:
        """
        Encrypt data.

        Args:
            plaintext: Data to encrypt.

        Returns:
            Base64-encoded ciphertext.
        """
        if isinstance(plaintext, str):
            plaintext = plaintext.encode()
        ciphertext = self._fernet.encrypt(plaintext)
        return ciphertext.decode()

    def decrypt(self, ciphertext: Union[str, bytes]) -> str:
        """
        Decrypt data.

        Args:
            ciphertext: Encrypted data.

        Returns:
            Decrypted plaintext.
        """
        if isinstance(ciphertext, str):
            ciphertext = ciphertext.encode()
        plaintext = self._fernet.decrypt(ciphertext)
        return plaintext.decode()

    def encrypt_dict(
        self,
        data: dict[str, Any],
        fields: list[str],
    ) -> dict[str, Any]:
        """
        Encrypt specific fields in a dictionary.

        Args:
            data: Dictionary with data.
            fields: List of field names to encrypt.

        Returns:
            Dictionary with encrypted fields.
        """
        result = data.copy()
        for field in fields:
            if field in result and result[field] is not None:
                result[field] = self.encrypt(str(result[field]))
        return result

    def decrypt_dict(
        self,
        data: dict[str, Any],
        fields: list[str],
    ) -> dict[str, Any]:
        """
        Decrypt specific fields in a dictionary.

        Args:
            data: Dictionary with encrypted data.
            fields: List of field names to decrypt.

        Returns:
            Dictionary with decrypted fields.
        """
        result = data.copy()
        for field in fields:
            if field in result and result[field] is not None:
                result[field] = self.decrypt(result[field])
        return result


class KeyRotation:
    """
    Key rotation manager for field encryption.

    Supports encrypting with current key while decrypting
    with multiple keys during rotation period.
    """

    def __init__(
        self,
        current_key: str,
        previous_keys: Optional[list[str]] = None,
    ):
        """
        Initialize with current and previous keys.

        Args:
            current_key: Current encryption key.
            previous_keys: List of previous keys (for decryption only).
        """
        self._current = FieldEncryption(key=current_key)
        self._previous = [
            FieldEncryption(key=k) for k in (previous_keys or [])
        ]

    def encrypt(self, plaintext: Union[str, bytes]) -> str:
        """Encrypt with current key."""
        return self._current.encrypt(plaintext)

    def decrypt(self, ciphertext: Union[str, bytes]) -> str:
        """
        Decrypt with current or previous keys.

        Tries current key first, then previous keys in order.
        """
        # Try current key
        try:
            return self._current.decrypt(ciphertext)
        except Exception:
            pass

        # Try previous keys
        for encryptor in self._previous:
            try:
                return encryptor.decrypt(ciphertext)
            except Exception:
                continue

        raise ValueError("Could not decrypt with any available key")

    def re_encrypt(self, ciphertext: Union[str, bytes]) -> str:
        """
        Re-encrypt data with current key.

        Useful for migrating data after key rotation.
        """
        plaintext = self.decrypt(ciphertext)
        return self.encrypt(plaintext)


class HashingUtility:
    """
    Utility for hashing sensitive data (one-way encryption).

    Use for data that needs to be compared but not retrieved
    (e.g., lookup tokens, fingerprints).
    """

    def __init__(self, salt: Optional[str] = None):
        """
        Initialize with optional salt.

        Args:
            salt: Salt for hashing (use environment variable in production).
        """
        self._salt = (salt or "").encode()

    def hash(self, data: Union[str, bytes]) -> str:
        """
        Create SHA-256 hash of data.

        Args:
            data: Data to hash.

        Returns:
            Hex-encoded hash.
        """
        if isinstance(data, str):
            data = data.encode()
        salted = self._salt + data
        return hashlib.sha256(salted).hexdigest()

    def hash_with_pepper(
        self,
        data: Union[str, bytes],
        pepper: str,
    ) -> str:
        """
        Create hash with additional pepper.

        Args:
            data: Data to hash.
            pepper: Additional secret value.

        Returns:
            Hex-encoded hash.
        """
        if isinstance(data, str):
            data = data.encode()
        peppered = self._salt + data + pepper.encode()
        return hashlib.sha256(peppered).hexdigest()

    def verify(self, data: Union[str, bytes], hash_value: str) -> bool:
        """
        Verify data against hash.

        Args:
            data: Data to verify.
            hash_value: Expected hash.

        Returns:
            True if match.
        """
        computed = self.hash(data)
        return secrets.compare_digest(computed, hash_value)
