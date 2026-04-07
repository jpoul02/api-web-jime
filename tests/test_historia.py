# tests/test_historia.py
import pytest
from unittest.mock import patch

MOCK_URL = "https://res.cloudinary.com/test/image/upload/test.jpg"


# ── Slides ─────────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_list_slides_empty(client):
    resp = await client.get("/historia/slides")
    assert resp.status_code == 200
    assert resp.json() == []


@pytest.mark.asyncio
async def test_create_slide_text_type(client):
    resp = await client.post(
        "/historia/slides",
        data={
            "date": "FINALES DE 2022",
            "title": "El Coro",
            "desc": "Nos conocimos en el coro.",
            "slide_type": "text",
        },
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["date"] == "FINALES DE 2022"
    assert data["title"] == "El Coro"
    assert data["type"] == "text"
    assert data["img_url"] is None
    assert data["order"] == 0


@pytest.mark.asyncio
async def test_create_slide_with_photo(client):
    with patch("app.routers.historia.maybe_upload", return_value=MOCK_URL):
        resp = await client.post(
            "/historia/slides",
            data={"date": "2023", "title": "Foto", "desc": "desc", "slide_type": "fullbleed"},
            files={"photo": ("test.jpg", b"fake", "image/jpeg")},
        )
    assert resp.status_code == 201
    assert resp.json()["img_url"] == MOCK_URL


@pytest.mark.asyncio
async def test_create_slide_order_increments(client):
    for i in range(3):
        resp = await client.post(
            "/historia/slides",
            data={"date": f"DATE {i}", "title": f"Title {i}", "desc": "d", "slide_type": "text"},
        )
        assert resp.json()["order"] == i


@pytest.mark.asyncio
async def test_list_slides_ordered(client):
    for i in range(3):
        await client.post(
            "/historia/slides",
            data={"date": f"DATE {i}", "title": f"Title {i}", "desc": "d", "slide_type": "text"},
        )
    resp = await client.get("/historia/slides")
    data = resp.json()
    assert len(data) == 3
    assert [s["order"] for s in data] == [0, 1, 2]


@pytest.mark.asyncio
async def test_update_slide(client):
    create_resp = await client.post(
        "/historia/slides",
        data={"date": "2022", "title": "Old", "desc": "d", "slide_type": "text"},
    )
    slide_id = create_resp.json()["id"]
    resp = await client.patch(f"/historia/slides/{slide_id}", data={"title": "New"})
    assert resp.status_code == 200
    assert resp.json()["title"] == "New"
    assert resp.json()["date"] == "2022"


@pytest.mark.asyncio
async def test_update_slide_not_found(client):
    resp = await client.patch("/historia/slides/9999", data={"title": "x"})
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_delete_slide(client):
    create_resp = await client.post(
        "/historia/slides",
        data={"date": "2022", "title": "T", "desc": "d", "slide_type": "text"},
    )
    slide_id = create_resp.json()["id"]
    del_resp = await client.delete(f"/historia/slides/{slide_id}")
    assert del_resp.status_code == 200
    assert del_resp.json() == {"ok": True}
    list_resp = await client.get("/historia/slides")
    assert list_resp.json() == []


@pytest.mark.asyncio
async def test_delete_slide_not_found(client):
    resp = await client.delete("/historia/slides/9999")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_reorder_slides(client):
    ids = []
    for i in range(3):
        r = await client.post(
            "/historia/slides",
            data={"date": f"D {i}", "title": f"T {i}", "desc": "d", "slide_type": "text"},
        )
        ids.append(r.json()["id"])
    reversed_ids = list(reversed(ids))
    resp = await client.post(
        "/historia/slides/reorder",
        json=reversed_ids,
        headers={"Content-Type": "application/json"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert [s["id"] for s in data] == reversed_ids


# ── Momentos Favoritos ─────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_list_momentos_empty(client):
    resp = await client.get("/historia/momentos")
    assert resp.status_code == 200
    assert resp.json() == []


@pytest.mark.asyncio
async def test_create_momento(client):
    with patch("app.routers.historia.maybe_upload", return_value=MOCK_URL):
        resp = await client.post(
            "/historia/momentos",
            files={"photo": ("photo.jpg", b"fake", "image/jpeg")},
        )
    assert resp.status_code == 201
    data = resp.json()
    assert data["photo_url"] == MOCK_URL
    assert data["order"] == 0


@pytest.mark.asyncio
async def test_create_momento_order_increments(client):
    with patch("app.routers.historia.maybe_upload", return_value=MOCK_URL):
        for i in range(3):
            resp = await client.post(
                "/historia/momentos",
                files={"photo": ("p.jpg", b"x", "image/jpeg")},
            )
            assert resp.json()["order"] == i


@pytest.mark.asyncio
async def test_delete_momento(client):
    with patch("app.routers.historia.maybe_upload", return_value=MOCK_URL):
        create_resp = await client.post(
            "/historia/momentos",
            files={"photo": ("p.jpg", b"x", "image/jpeg")},
        )
    mid = create_resp.json()["id"]
    del_resp = await client.delete(f"/historia/momentos/{mid}")
    assert del_resp.status_code == 200
    assert del_resp.json() == {"ok": True}
    list_resp = await client.get("/historia/momentos")
    assert list_resp.json() == []


@pytest.mark.asyncio
async def test_delete_momento_not_found(client):
    resp = await client.delete("/historia/momentos/9999")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_reorder_momentos(client):
    ids = []
    with patch("app.routers.historia.maybe_upload", return_value=MOCK_URL):
        for i in range(3):
            r = await client.post(
                "/historia/momentos",
                files={"photo": ("p.jpg", b"x", "image/jpeg")},
            )
            ids.append(r.json()["id"])
    reversed_ids = list(reversed(ids))
    resp = await client.post(
        "/historia/momentos/reorder",
        json=reversed_ids,
        headers={"Content-Type": "application/json"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert [m["id"] for m in data] == reversed_ids
