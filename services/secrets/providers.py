"""
Secrets backend abstraction.

Supports AWS Secrets Manager, HashiCorp Vault, GCP Secret Manager,
and Azure Key Vault behind a minimal ``ISecretsBackend`` interface.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Optional

from loguru import logger

from configurations.secrets import SecretsConfiguration
from core.utils.optional_imports import optional_import

boto3, _ = optional_import("boto3")
hvac, _ = optional_import("hvac")
gcp_secretmanager, _ = optional_import("google.cloud.secretmanager")
_azure_identity, ClientSecretCredential = optional_import("azure.identity", "ClientSecretCredential")
_azure_kv, SecretClient = optional_import("azure.keyvault.secrets", "SecretClient")


class ISecretsBackend(ABC):
    """
    Minimal secrets backend interface.
    """

    @abstractmethod
    async def get_secret(self, name: str) -> Optional[str]:  # pragma: no cover - interface
        raise NotImplementedError


class AwsSecretsManagerBackend(ISecretsBackend):
    def __init__(self, region: str, access_key_id: Optional[str], secret_access_key: Optional[str], prefix: str) -> None:
        if boto3 is None:  # pragma: no cover - optional
            raise RuntimeError("boto3 is not installed")
        kwargs = {"region_name": region}
        if access_key_id and secret_access_key:
            kwargs.update(
                aws_access_key_id=access_key_id,
                aws_secret_access_key=secret_access_key,
            )
        self._client = boto3.client("secretsmanager", **kwargs)
        self._prefix = prefix.rstrip("/") if prefix else ""

    async def get_secret(self, name: str) -> Optional[str]:
        full_name = f"{self._prefix}/{name}" if self._prefix else name
        try:
            resp = self._client.get_secret_value(SecretId=full_name)
            return resp.get("SecretString")
        except Exception as exc:  # pragma: no cover - defensive
            logger.warning("AWS Secrets Manager error for %s: %s", full_name, exc)
            return None


class VaultBackend(ISecretsBackend):
    def __init__(self, url: str, token: Optional[str], mount_point: str) -> None:
        if hvac is None:  # pragma: no cover - optional
            raise RuntimeError("hvac (Vault client) is not installed")
        self._client = hvac.Client(url=url, token=token)
        self._mount_point = mount_point

    async def get_secret(self, name: str) -> Optional[str]:
        try:
            resp = self._client.secrets.kv.v2.read_secret_version(
                path=name,
                mount_point=self._mount_point,
            )
            data = resp.get("data", {}).get("data", {})
            # For simplicity, return JSON string; apps can parse as needed
            import json

            return json.dumps(data)
        except Exception as exc:  # pragma: no cover - defensive
            logger.warning("Vault error for %s: %s", name, exc)
            return None


class GcpSecretsManagerBackend(ISecretsBackend):
    def __init__(self, project_id: str, credentials_json_path: Optional[str]) -> None:
        if gcp_secretmanager is None:  # pragma: no cover - optional
            raise RuntimeError("google-cloud-secret-manager is not installed")
        if credentials_json_path:
            from google.oauth2 import service_account

            creds = service_account.Credentials.from_service_account_file(credentials_json_path)
            self._client = gcp_secretmanager.SecretManagerServiceClient(credentials=creds)
        else:
            self._client = gcp_secretmanager.SecretManagerServiceClient()
        self._project_id = project_id

    async def get_secret(self, name: str) -> Optional[str]:
        try:
            resource_name = f"projects/{self._project_id}/secrets/{name}/versions/latest"
            resp = self._client.access_secret_version(name=resource_name)
            return resp.payload.data.decode("utf-8")
        except Exception as exc:  # pragma: no cover - defensive
            logger.warning("GCP Secret Manager error for %s: %s", name, exc)
            return None


class AzureKeyVaultBackend(ISecretsBackend):
    def __init__(self, vault_url: str, client_id: Optional[str], client_secret: Optional[str], tenant_id: Optional[str]) -> None:
        if SecretClient is None or ClientSecretCredential is None:  # pragma: no cover - optional
            raise RuntimeError("azure-identity and azure-keyvault-secrets are not installed")
        if client_id and client_secret and tenant_id:
            credential = ClientSecretCredential(
                tenant_id=tenant_id,
                client_id=client_id,
                client_secret=client_secret,
            )
        else:
            from azure.identity import DefaultAzureCredential

            credential = DefaultAzureCredential()
        self._client = SecretClient(vault_url=vault_url, credential=credential)

    async def get_secret(self, name: str) -> Optional[str]:
        try:
            secret = self._client.get_secret(name)
            return secret.value
        except Exception as exc:  # pragma: no cover - defensive
            logger.warning("Azure Key Vault error for %s: %s", name, exc)
            return None


def build_secrets_backend() -> Optional[ISecretsBackend]:
    """
    Build an appropriate secrets backend from configuration.

    Priority:
      - Vault
      - AWS Secrets Manager
      - GCP Secret Manager
      - Azure Key Vault
    """

    cfg = SecretsConfiguration.instance().get_config()

    if cfg.vault.enabled:
        try:
            return VaultBackend(
                url=cfg.vault.url,
                token=cfg.vault.token,
                mount_point=cfg.vault.mount_point,
            )
        except Exception as exc:  # pragma: no cover - defensive
            logger.warning("Failed to initialize Vault backend: %s", exc)

    if cfg.aws.enabled:
        try:
            return AwsSecretsManagerBackend(
                region=cfg.aws.region,
                access_key_id=cfg.aws.access_key_id,
                secret_access_key=cfg.aws.secret_access_key,
                prefix=cfg.aws.prefix,
            )
        except Exception as exc:  # pragma: no cover - defensive
            logger.warning("Failed to initialize AWS Secrets Manager backend: %s", exc)

    if cfg.gcp.enabled and cfg.gcp.project_id:
        try:
            return GcpSecretsManagerBackend(
                project_id=cfg.gcp.project_id,
                credentials_json_path=cfg.gcp.credentials_json_path,
            )
        except Exception as exc:  # pragma: no cover - defensive
            logger.warning("Failed to initialize GCP Secret Manager backend: %s", exc)

    if cfg.azure.enabled and cfg.azure.vault_url:
        try:
            return AzureKeyVaultBackend(
                vault_url=cfg.azure.vault_url,
                client_id=cfg.azure.client_id,
                client_secret=cfg.azure.client_secret,
                tenant_id=cfg.azure.tenant_id,
            )
        except Exception as exc:  # pragma: no cover - defensive
            logger.warning("Failed to initialize Azure Key Vault backend: %s", exc)

    logger.info("No secrets backend is enabled.")
    return None


__all__ = [
    "ISecretsBackend",
    "AwsSecretsManagerBackend",
    "VaultBackend",
    "GcpSecretsManagerBackend",
    "AzureKeyVaultBackend",
    "build_secrets_backend",
]

