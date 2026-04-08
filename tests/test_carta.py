# tests/test_carta.py
import pytest

@pytest.mark.asyncio
async def test_get_carta_empty(client):
    resp = await client.get("/carta")
    assert resp.status_code == 200
    assert resp.json() == {"texto": None}

@pytest.mark.asyncio
async def test_put_carta(client):
    resp = await client.put(
        "/carta",
        json={"texto": "Querida Jimena, esta es mi carta para vos."},
    )
    assert resp.status_code == 200
    assert resp.json()["texto"] == "Querida Jimena, esta es mi carta para vos."

@pytest.mark.asyncio
async def test_get_carta_after_put(client):
    await client.put("/carta", json={"texto": "Primera versión"})
    resp = await client.get("/carta")
    assert resp.json()["texto"] == "Primera versión"

@pytest.mark.asyncio
async def test_put_carta_updates_existing(client):
    await client.put("/carta", json={"texto": "Versión 1"})
    await client.put("/carta", json={"texto": "Versión 2"})
    resp = await client.get("/carta")
    assert resp.json()["texto"] == "Versión 2"
