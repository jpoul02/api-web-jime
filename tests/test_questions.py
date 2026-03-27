# tests/test_questions.py
import pytest

@pytest.mark.asyncio
async def test_get_random_questions_default_count(client):
    resp = await client.get("/questions/random?count=5")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 5
    assert all("id" in q and "text" in q for q in data)

@pytest.mark.asyncio
async def test_get_random_questions_exclude(client):
    resp = await client.get("/questions/random?count=3&exclude=1,2")
    assert resp.status_code == 200
    data = resp.json()
    ids = [q["id"] for q in data]
    assert 1 not in ids
    assert 2 not in ids

@pytest.mark.asyncio
async def test_get_random_questions_no_duplicates(client):
    resp = await client.get("/questions/random?count=5")
    data = resp.json()
    ids = [q["id"] for q in data]
    assert len(ids) == len(set(ids))
