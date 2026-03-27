# tests/test_postales.py
import pytest
import json
from unittest.mock import patch, AsyncMock

MOCK_URL = "https://pub-test.r2.dev/test.jpg"

@pytest.mark.asyncio
async def test_create_postal_minimal(client):
    with patch("app.routers.postales.upload_file", return_value=MOCK_URL):
        resp = await client.post(
            "/postales",
            data={
                "name": "Sofi",
                "answers": json.dumps([{"question_id": 1, "answer_text": "Mi respuesta"}]),
            },
        )
    assert resp.status_code == 201
    data = resp.json()
    assert data["name"] == "Sofi"
    assert data["id"] is not None
    assert len(data["answers"]) == 1

@pytest.mark.asyncio
async def test_list_postales(client):
    with patch("app.routers.postales.upload_file", return_value=MOCK_URL):
        await client.post(
            "/postales",
            data={"name": "Caro", "answers": json.dumps([])},
        )
    resp = await client.get("/postales")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) >= 1
    assert "id" in data[0]
    assert "name" in data[0]

@pytest.mark.asyncio
async def test_get_postal_by_id(client):
    with patch("app.routers.postales.upload_file", return_value=MOCK_URL):
        create_resp = await client.post(
            "/postales",
            data={"name": "Vale", "answers": json.dumps([])},
        )
    postal_id = create_resp.json()["id"]
    resp = await client.get(f"/postales/{postal_id}")
    assert resp.status_code == 200
    assert resp.json()["id"] == postal_id

@pytest.mark.asyncio
async def test_get_postal_not_found(client):
    resp = await client.get("/postales/99999")
    assert resp.status_code == 404
