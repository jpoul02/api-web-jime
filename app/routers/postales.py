# app/routers/postales.py
import json
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app import crud
from app.schemas import PostalOut, PostalListItem, AnswerIn
from app.storage import upload_file

router = APIRouter(prefix="/postales", tags=["postales"])

@router.post("", response_model=PostalOut, status_code=201)
async def create_postal(
    name: str = Form(...),
    answers: str = Form(default="[]"),
    profile_photo: UploadFile | None = File(default=None),
    video: UploadFile | None = File(default=None),
    photos: list[UploadFile] = File(default=[]),
    db: AsyncSession = Depends(get_db),
):
    profile_photo_url = await upload_file(profile_photo, "profiles") if profile_photo else None
    video_url = await upload_file(video, "videos") if video else None
    photo_urls = [await upload_file(p, "photos") for p in photos if p.size]
    answers_parsed = [AnswerIn(**a) for a in json.loads(answers)]
    return await crud.create_postal(db, name, profile_photo_url, video_url, answers_parsed, photo_urls)

@router.get("", response_model=list[PostalListItem])
async def list_postales(db: AsyncSession = Depends(get_db)):
    return await crud.get_postales(db)

@router.get("/{postal_id}", response_model=PostalOut)
async def get_postal(postal_id: int, db: AsyncSession = Depends(get_db)):
    postal = await crud.get_postal(db, postal_id)
    if not postal:
        raise HTTPException(status_code=404, detail="Postal not found")
    return postal
