from sqlalchemy import event

from app.extensions import db


def create_product(client, sku="SKU-001", stock=10):
    return client.post("/api/v1/products", json={
        "sku": sku, "name": "Widget", "price_cents": 1250, "qty_in_stock": stock,
    })


def test_product_post_get_and_pagination(client):
    created = create_product(client)
    assert created.status_code == 201
    product_id = created.json["id"]
    assert created.json["qty_in_stock"] == 10

    fetched = client.get(f"/api/v1/products/{product_id}")
    assert fetched.status_code == 200
    assert fetched.json["sku"] == "SKU-001"

    page = client.get("/api/v1/products?page=1&size=1")
    assert page.status_code == 200
    assert page.json["total"] == 1
    assert len(page.json["items"]) == 1


def test_duplicate_sku_validation_reserve_and_soft_delete(client):
    product = create_product(client)
    assert create_product(client).status_code == 409
    assert client.post(f"/api/v1/products/{product.json['id']}/reserve", json={"qty": 3}).json["qty_in_stock"] == 7
    assert client.post(f"/api/v1/products/{product.json['id']}/reserve", json={"qty": 99}).status_code == 409
    assert client.delete(f"/api/v1/products/{product.json['id']}").status_code == 204
    assert client.get(f"/api/v1/products/{product.json['id']}").status_code == 404


def test_orders_link_multiple_products_and_eager_load(client, app):
    first = create_product(client, "SKU-101", stock=20).json
    second = create_product(client, "SKU-102", stock=20).json
    for i in range(8):
        response = client.post("/api/v1/orders", json={"items": [
            {"product_id": first["id"], "quantity": 1},
            {"product_id": second["id"], "quantity": 2},
        ]})
        assert response.status_code == 201
        assert len(response.json["items"]) == 2
        assert {line["product_id"] for line in response.json["items"]} == {first["id"], second["id"]}

    statements = []
    def record_sql(conn, cursor, statement, parameters, context, executemany):
        if statement.lstrip().upper().startswith("SELECT"):
            statements.append(statement)

    with app.app_context():
        event.listen(db.engine, "before_cursor_execute", record_sql)
        try:
            response = client.get("/api/v1/orders")
        finally:
            event.remove(db.engine, "before_cursor_execute", record_sql)

    assert response.status_code == 200
    assert len(response.json) == 8
    # Orders plus their line items and products are loaded in a fixed query count.
    assert len(statements) <= 2


def test_order_item_crud_updates_inventory(client):
    product = create_product(client, "SKU-201", stock=10).json
    order = client.post("/api/v1/orders", json={"items": [
        {"product_id": product["id"], "quantity": 2}
    ]})
    assert order.status_code == 201
    order_id = order.json["id"]
    item_id = order.json["items"][0]["id"]
    assert order.json["items"][0]["product"]["sku"] == "SKU-201"

    changed = client.patch(f"/api/v1/orders/{order_id}/items/{item_id}", json={"quantity": 4})
    assert changed.status_code == 200
    assert changed.json["quantity"] == 4
    assert client.get(f"/api/v1/orders/{order_id}/items/{item_id}").status_code == 200
    assert client.delete(f"/api/v1/orders/{order_id}/items/{item_id}").status_code == 204
    assert client.get(f"/api/v1/orders/{order_id}/items").json == []


def test_health_and_readiness_are_separate(client):
    assert client.get("/healthz").json == {"status": "ok"}
    assert client.get("/ready").json["checks"]["database"] == "ok"
