"""Independent Kafka consumer that maintains aggregate order analytics."""

import json
import os
from typing import Any

from kafka import KafkaConsumer

from backend.storage import data_directory, read_json, write_json


def update_analytics(order: dict[str, Any], directory=None) -> dict[str, int | float]:
    """Add an order's submitted amount to the persisted aggregate."""
    target_directory = directory or data_directory()
    analytics_path = target_directory / "analytics.json"
    analytics = read_json(analytics_path, {"total_orders": 0, "total_revenue": 0})
    if not isinstance(analytics, dict):
        analytics = {"total_orders": 0, "total_revenue": 0}
    result = {
        "total_orders": int(analytics.get("total_orders", 0)) + 1,
        "total_revenue": analytics.get("total_revenue", 0) + order["amount"],
    }
    write_json(analytics_path, result)
    print(f"[ANALYTICS CONSUMER] Updated totals for {order['order_id']}", flush=True)
    return result


def main() -> None:
    consumer = KafkaConsumer(
        "orders",
        bootstrap_servers=os.environ.get("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092"),
        group_id="analytics-processors",
        auto_offset_reset="earliest",
        enable_auto_commit=True,
        value_deserializer=lambda value: json.loads(value.decode("utf-8")),
    )
    print("[ANALYTICS CONSUMER] Waiting for orders", flush=True)
    for message in consumer:
        update_analytics(message.value)


if __name__ == "__main__":
    main()
