"""Kafka consumer that stores the processed order projection."""

import json
import os
from typing import Any

from kafka import KafkaConsumer

from backend.storage import data_directory, read_json, write_json


def process_order(order: dict[str, Any], directory=None) -> None:
    """Persist one order, ignoring redelivery of an already stored order ID."""
    target_directory = directory or data_directory()
    orders_path = target_directory / "orders.json"
    orders = read_json(orders_path, [])
    if not isinstance(orders, list):
        orders = []
    if any(item.get("order_id") == order.get("order_id") for item in orders if isinstance(item, dict)):
        return
    orders.append(order)
    write_json(orders_path, orders)
    print(f"[ORDER CONSUMER] Processed {order['order_id']}", flush=True)


def main() -> None:
    consumer = KafkaConsumer(
        "orders",
        bootstrap_servers=os.environ.get("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092"),
        group_id="order-processors",
        auto_offset_reset="earliest",
        enable_auto_commit=True,
        value_deserializer=lambda value: json.loads(value.decode("utf-8")),
    )
    print("[ORDER CONSUMER] Waiting for orders", flush=True)
    for message in consumer:
        process_order(message.value)


if __name__ == "__main__":
    main()
