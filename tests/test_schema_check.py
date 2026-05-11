from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


USER_SCHEMA = {
    "type": "object",
    "required": ["name", "age"],
    "properties": {
        "name": {"type": "string"},
        "age": {"type": "integer", "minimum": 0},
        "role": {"type": "string", "enum": ["admin", "user"]},
    },
    "additionalProperties": False,
}


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_valid_payload():
    response = client.post("/v1/schema-check", json={"json_schema": USER_SCHEMA, "payload": {"name": "Gary", "age": 42}})
    assert response.status_code == 200
    body = response.json()
    assert body["valid"] is True
    assert body["errors"] == []
    assert body["confidence"] == 1.0


def test_missing_required_field():
    response = client.post("/v1/schema-check", json={"json_schema": USER_SCHEMA, "payload": {"name": "Gary"}})
    assert response.status_code == 200
    body = response.json()
    assert body["valid"] is False
    assert body["errors"][0]["code"] == "REQUIRED_FIELD_MISSING"


def test_type_mismatch():
    response = client.post("/v1/schema-check", json={"json_schema": USER_SCHEMA, "payload": {"name": "Gary", "age": "old"}})
    assert response.status_code == 200
    body = response.json()
    assert body["valid"] is False
    assert any(error["code"] == "TYPE_MISMATCH" for error in body["errors"])


def test_additional_property():
    response = client.post("/v1/schema-check", json={"json_schema": USER_SCHEMA, "payload": {"name": "Gary", "age": 42, "extra": True}})
    assert response.status_code == 200
    body = response.json()
    assert body["valid"] is False
    assert any(error["code"] == "ADDITIONAL_PROPERTY" for error in body["errors"])


def test_invalid_schema_returns_400():
    response = client.post("/v1/schema-check", json={"json_schema": {"type": "not-a-type"}, "payload": {}})
    assert response.status_code == 400
    assert response.json()["detail"]["code"] == "INVALID_JSON_SCHEMA"


def test_repair_missing_required_field():
    response = client.post(
        "/v1/schema-check",
        json={"json_schema": USER_SCHEMA, "payload": {"name": "Gary"}, "repair": True},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["valid"] is False
    assert body["suggested_payload"]["age"] == 0
