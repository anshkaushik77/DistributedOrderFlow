import json

import pytest

from backend.app import create_app
from consumer.analytics_consumer import update_analytics


@pytest.fixture

def client(tmp_path, monkeypatch):
    published = []
    monkeypatch.setattr("backend.app.publish_order", published.append)
    app = create_app({"TESTING": True, "DATA_DIR": str(tmp_path)})
    app.config["PUBLISHED_ORDERS"] = published
    return app.test_client(), published, tmp_path


def test_valid_order_is_published_and_returns_id(client):
    test_client, published, _ = client

    response = test_client.post(
        "/orders", json={"product": "Laptop", "quantity": 2, "amount": 50000}
    )

    assert response.status_code == 201
    assert response.get_json() == {
        "message": "Order created successfully",
        "order_id": "ORD001",
    }
    assert published == [
        {"order_id": "ORD001", "product": "Laptop", "quantity": 2, "amount": 50000}
    ]


def test_missing_product_is_rejected(client):
    test_client, published, _ = client

    response = test_client.post("/orders", json={"quantity": 1, "amount": 100})

    assert response.status_code == 400
    assert response.get_json()["error"] == "Product is required"
    assert published == []


def test_invalid_quantity_is_rejected(client):
    test_client, published, _ = client

    response = test_client.post(
        "/orders", json={"product": "Phone", "quantity": 0, "amount": 100}
    )

    assert response.status_code == 400
    assert "Quantity" in response.get_json()["error"]
    assert published == []


@pytest.mark.parametrize("amount", [0, -1, "100", None])
def test_invalid_amount_is_rejected(client, amount):
    test_client, published, _ = client

    response = test_client.post(
        "/orders", json={"product": "Phone", "quantity": 1, "amount": amount}
    )

    assert response.status_code == 400
    assert "Amount" in response.get_json()["error"]
    assert published == []


def test_analytics_consumer_accumulates_order_amounts(tmp_path):
    first = update_analytics(
        {"order_id": "ORD001", "product": "Laptop", "quantity": 2, "amount": 50000},
        tmp_path,
    )
    second = update_analytics(
        {"order_id": "ORD002", "product": "Phone", "quantity": 1, "amount": 35000},
        tmp_path,
    )

    assert first == {"total_orders": 1, "total_revenue": 50000}
    assert second == {"total_orders": 2, "total_revenue": 85000}
    with (tmp_path / "analytics.json").open(encoding="utf-8") as file:
        assert json.load(file) == second


def test_get_endpoints_return_consumer_data(client):
    test_client, _, directory = client
    (directory / "orders.json").write_text(
        '[{"order_id":"ORD001","product":"Laptop","quantity":2,"amount":50000}]',
        encoding="utf-8",
    )
    (directory / "analytics.json").write_text(
        '{"total_orders":1,"total_revenue":50000}', encoding="utf-8"
    )

    assert test_client.get("/orders").get_json()[0]["order_id"] == "ORD001"
    assert test_client.get("/analytics").get_json() == {
        "total_orders": 1,
        "total_revenue": 50000,
    }
