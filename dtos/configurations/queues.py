"""
Configuration DTOs for message queues and pub/sub backends.

Covers RabbitMQ, Amazon SQS, and NATS. These map to
``config/queues/config.json``.
"""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel


class RabbitMQConfigDTO(BaseModel):
    enabled: bool = False
    url: Optional[str] = "amqp://guest:guest@localhost:5672//"
    exchange: str = "fastmvc"
    default_routing_key: str = "events"


class SQSConfigDTO(BaseModel):
    enabled: bool = False
    region: str = "us-east-1"
    queue_url: Optional[str] = None
    access_key_id: Optional[str] = None
    secret_access_key: Optional[str] = None


class NATSConfigDTO(BaseModel):
    enabled: bool = False
    servers: list[str] = ["nats://127.0.0.1:4222"]
    stream: str = "fastmvc"
    subject: str = "events"


class AzureServiceBusConfigDTO(BaseModel):
    enabled: bool = False
    connection_string: Optional[str] = None
    queue_name: Optional[str] = None


class QueuesConfigurationDTO(BaseModel):
    """
    Aggregated configuration for all queue backends.
    """

    rabbitmq: RabbitMQConfigDTO = RabbitMQConfigDTO()
    sqs: SQSConfigDTO = SQSConfigDTO()
    nats: NATSConfigDTO = NATSConfigDTO()
    service_bus: AzureServiceBusConfigDTO = AzureServiceBusConfigDTO()


__all__ = [
    "RabbitMQConfigDTO",
    "SQSConfigDTO",
    "NATSConfigDTO",
    "AzureServiceBusConfigDTO",
    "QueuesConfigurationDTO",
]

