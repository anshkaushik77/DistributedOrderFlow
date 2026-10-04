"""Kafka publishing boundary used by the Flask API."""

import json
import os
from typing import Any

from kafka import KafkaProducer

_producer: KafkaProducer | None = None


def _get_producer() -> KafkaProducer:
    global _producer
    if _producer is None:
        _producer = KafkaProducer(
            bootstrap_servers=os.environ.get("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092"),
            value_serializer=lambda value: json.dumps(value).encode("utf-8"),
            acks="all",
            retries=5,
            request_timeout_ms=10000,
            max_block_ms=10000,
        )
    return _producer


def publish_order(order: dict[str, Any]) -> None:
    """Publish an order and wait for broker acknowledgement."""
    _get_producer().send("orders", order).get(timeout=15)
