import importlib

from fastapi.testclient import TestClient


USER_SCHEMA = {
    "type": "object",
    "required": ["name"],
    "properties": {"name": {"type": "string"}},
}


def _reload_app(monkeypatch, payment_mode: str, **env):
    monkeypatch.setenv("SCHEMACHECK_PAYMENT_MODE", payment_mode)
    for key, value in env.items():
        monkeypatch.setenv(key, value)

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


def test_x402_payment_gate_requires_pay_to(monkeypatch):
    app = _reload_app(monkeypatch, "x402", SCHEMACHECK_X402_PAY_TO="")
    client = TestClient(app)
    response = client.post("/v1/schema-check", json={"json_schema": USER_SCHEMA, "payload": {"name": "Gary"}})
    assert response.status_code == 500
    assert response.json()["detail"]["code"] == "X402_PAY_TO_MISSING"


def test_x402_payment_gate_returns_402_with_requirements(monkeypatch):
    app = _reload_app(monkeypatch, "x402")
    client = TestClient(app)
    response = client.post("/v1/schema-check", json={"json_schema": USER_SCHEMA, "payload": {"name": "Gary"}})
    assert response.status_code == 402
    detail = response.json()["detail"]
    assert detail["code"] == "PAYMENT_REQUIRED"
    assert detail["payment_protocol"] == "x402"
    assert detail["payment_header"] == "X-PAYMENT"
    assert detail["payment_requirements"]["network"] == "eip155:84532"
    assert detail["payment_requirements"]["payTo"] == "0x8fC4006534801c17A3368075A1Fb3b3C511EdB1F"
    assert "PAYMENT-REQUIRED" in response.headers


def test_x402_payment_payload_is_guarded_until_live_verification_enabled(monkeypatch):
    app = _reload_app(monkeypatch, "x402", SCHEMACHECK_X402_REAL_VERIFICATION_ENABLED="false")
    client = TestClient(app)
    response = client.post(
        "/v1/schema-check",
        headers={"X-PAYMENT": "test-payment-payload"},
        json={"json_schema": USER_SCHEMA, "payload": {"name": "Gary"}},
    )
    assert response.status_code == 501
    assert response.json()["detail"]["code"] == "X402_REAL_VERIFICATION_DISABLED"
