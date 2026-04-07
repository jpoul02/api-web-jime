# app/routers/historia.py
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app import crud
from app.schemas import HistoriaSlideOut, MomentoFavoritoOut
from app.storage import maybe_upload

router = APIRouter(prefix="/historia", tags=["historia"])

# ── Slides ─────────────────────────────────────────────────────────────────────

@router.get("/slides", response_model=list[HistoriaSlideOut])
async def list_slides(db: AsyncSession = Depends(get_db)):
    return await crud.get_historia_slides(db)

@router.post("/slides/reorder")
async def reorder_slides(ids: list[int], db: AsyncSession = Depends(get_db)):
    return await crud.reorder_historia_slides(db, ids)

@router.post("/slides", response_model=HistoriaSlideOut, status_code=201)
async def create_slide(
    date: str = Form(...),
    title: str = Form(...),
    desc: str = Form(...),
    type: str = Form(...),
    emoji: str | None = Form(None),
    photo: UploadFile | None = File(None),
    db: AsyncSession = Depends(get_db),
):
    img_url = await maybe_upload(photo, "historia/slides") if photo else None
    return await crud.create_historia_slide(db, date, title, desc, type, img_url, emoji)

@router.patch("/slides/{slide_id}", response_model=HistoriaSlideOut)
async def update_slide(
    slide_id: int,
    date: str | None = Form(None),
    title: str | None = Form(None),
    desc: str | None = Form(None),
    type: str | None = Form(None),
    emoji: str | None = Form(None),
    photo: UploadFile | None = File(None),
    db: AsyncSession = Depends(get_db),
):
    img_url = await maybe_upload(photo, "historia/slides") if photo else None
    slide = await crud.update_historia_slide(db, slide_id, date, title, desc, type, img_url, emoji)
    if not slide:
        raise HTTPException(404, "Slide no encontrado")
    return slide

@router.delete("/slides/{slide_id}")
async def delete_slide(slide_id: int, db: AsyncSession = Depends(get_db)):
    ok = await crud.delete_historia_slide(db, slide_id)
    if not ok:
        raise HTTPException(404, "Slide no encontrado")
    return {"ok": True}

# ── Momentos Favoritos ─────────────────────────────────────────────────────────

@router.get("/momentos", response_model=list[MomentoFavoritoOut])
async def list_momentos(db: AsyncSession = Depends(get_db)):
    return await crud.get_momentos_favoritos(db)

@router.post("/momentos/reorder")
async def reorder_momentos(ids: list[int], db: AsyncSession = Depends(get_db)):
    return await crud.reorder_momentos_favoritos(db, ids)

@router.post("/momentos", response_model=MomentoFavoritoOut, status_code=201)
async def create_momento(
    photo: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
):
    photo_url = await maybe_upload(photo, "historia/momentos")
    if not photo_url:
        raise HTTPException(400, "Se requiere una foto")
    return await crud.create_momento_favorito(db, photo_url)

@router.delete("/momentos/{momento_id}")
async def delete_momento(momento_id: int, db: AsyncSession = Depends(get_db)):
    ok = await crud.delete_momento_favorito(db, momento_id)
    if not ok:
        raise HTTPException(404, "Momento no encontrado")
    return {"ok": True}
