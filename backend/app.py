"""Flask API for creating orders and reading consumer-owned JSON projections."""

import math
import threading
from pathlib import Path
from typing import Any

from flask import Flask, jsonify, request

from backend.kafka_producer import publish_order
from backend.storage import data_directory, read_json, write_json

_sequence_lock = threading.Lock()


def _next_order_id(directory: Path) -> str:
    """Allocate the next human-readable ID, including before consumers catch up."""
    sequence_path = directory / "order_sequence.json"
    with _sequence_lock:
        sequence = read_json(sequence_path, {})
        last_id = sequence.get("last_id", 0) if isinstance(sequence, dict) else 0
        if not last_id:
            orders = read_json(directory / "orders.json", [])
            if isinstance(orders, list):
                for order in orders:
                    order_id = order.get("order_id", "") if isinstance(order, dict) else ""
                    if order_id.startswith("ORD") and order_id[3:].isdigit():
                        last_id = max(last_id, int(order_id[3:]))
        next_id = int(last_id) + 1
        write_json(sequence_path, {"last_id": next_id})
    return f"ORD{next_id:03d}"


def _valid_order(payload: Any) -> tuple[dict[str, Any] | None, str | None]:
    if not isinstance(payload, dict):
        return None, "Request body must be a JSON object"

    product = payload.get("product")
    if not isinstance(product, str) or not product.strip():
        return None, "Product is required"

    quantity = payload.get("quantity")
    if isinstance(quantity, bool) or not isinstance(quantity, int) or quantity <= 0:
        return None, "Quantity must be a positive integer"

    amount = payload.get("amount")
    if isinstance(amount, bool) or not isinstance(amount, (int, float)):
        return None, "Amount must be a positive number"
    if amount <= 0 or (isinstance(amount, float) and not math.isfinite(amount)):
        return None, "Amount must be a positive number"

    return {"product": product.strip(), "quantity": quantity, "amount": amount}, None


def create_app(test_config: dict[str, Any] | None = None) -> Flask:
    app = Flask(__name__)
    app.config["DATA_DIR"] = str(data_directory())
    if test_config:
        app.config.update(test_config)

    @app.post("/orders")
    def create_order():
        order_details, error = _valid_order(request.get_json(silent=True))
        if error:
            return jsonify({"error": error}), 400

        order = {"order_id": _next_order_id(Path(app.config["DATA_DIR"])), **order_details}
        try:
            publish_order(order)
        except Exception:
            app.logger.exception("Unable to publish order to Kafka")
            return jsonify({"error": "Kafka is unavailable; order was not sent"}), 503

        return jsonify({"message": "Order created successfully", "order_id": order["order_id"]}), 201

    @app.get("/orders")
    def get_orders():
        orders = read_json(Path(app.config["DATA_DIR"]) / "orders.json", [])
        return jsonify(orders if isinstance(orders, list) else [])

    @app.get("/analytics")
    def get_analytics():
        analytics = read_json(
            Path(app.config["DATA_DIR"]) / "analytics.json",
            {"total_orders": 0, "total_revenue": 0},
        )
        if not isinstance(analytics, dict):
            analytics = {"total_orders": 0, "total_revenue": 0}
        return jsonify(analytics)

    return app


app = create_app()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
