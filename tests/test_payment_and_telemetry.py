import importlib

from fastapi.testclient import TestClient


USER_SCHEMA = {
    "type": "object",
    "required": ["name"],
    "properties": {"name": {"type": "string"}},
}


def _reload_app(monkeypatch, payment_mode: str):
    monkeypatch.setenv("SCHEMACHECK_PAYMENT_MODE", payment_mode)
    import app.config
    import app.payment
    import app.main

    importlib.reload(app.config)
    importlib.reload(app.payment)
    importlib.reload(app.main)
    return app.main.app


def test_payment_gate_disabled_by_default(monkeypatch):
    app = _reload_app(monkeypatch, "disabled")
    client = TestClient(app)
    response = client.post("/v1/schema-check", json={"json_schema": USER_SCHEMA, "payload": {"name": "Gary"}})
    assert response.status_code == 200
    assert response.json()["valid"] is True


def test_placeholder_payment_gate_requires_token(monkeypatch):
    app = _reload_app(monkeypatch, "placeholder")
    client = TestClient(app)
    response = client.post("/v1/schema-check", json={"json_schema": USER_SCHEMA, "payload": {"name": "Gary"}})
    assert response.status_code == 402
    assert response.json()["detail"]["code"] == "PAYMENT_REQUIRED"


def test_placeholder_payment_gate_accepts_test_token(monkeypatch):
    app = _reload_app(monkeypatch, "placeholder")
    client = TestClient(app)
    response = client.post(
        "/v1/schema-check",
        headers={"X-Payment-Token": "test-payment-token"},
        json={"json_schema": USER_SCHEMA, "payload": {"name": "Gary"}},
    )
    assert response.status_code == 200
    assert response.json()["valid"] is True


def test_request_id_response_header(monkeypatch):
    app = _reload_app(monkeypatch, "disabled")
    client = TestClient(app)
    response = client.get("/health", headers={"X-Request-ID": "req-test-123"})
    assert response.status_code == 200
    assert response.headers["X-Request-ID"] == "req-test-123"
