# app/routers/postales.py
import asyncio
import json
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app import crud
from app.schemas import PostalOut, PostalListItem, FeedItem, AnswerIn, AnswerFeedItem, AskStats, VideoPostalItem, AnswerMediaOut
from app.storage import upload_file, maybe_upload

router = APIRouter(prefix="/postales", tags=["postales"])

@router.post("", response_model=PostalOut, status_code=201)
async def create_postal(
    name: str = Form(...),
    dedicatoria: str | None = Form(default=None),
    answers: str = Form(default="[]"),
    profile_photo: UploadFile | None = File(default=None),
    video: UploadFile | None = File(default=None),
    photos: list[UploadFile] = File(default=[]),
    db: AsyncSession = Depends(get_db),
):
    valid_photos = [p for p in photos if p.size]

    results = await asyncio.gather(
        maybe_upload(profile_photo, "profiles"),
        maybe_upload(video, "videos"),
        *[upload_file(p, "photos") for p in valid_photos],
    )

    profile_photo_url = results[0]
    video_url = results[1]
    photo_urls = list(results[2:])

    answers_parsed = [AnswerIn(**a) for a in json.loads(answers)]
    return await crud.create_postal(
        db, name, dedicatoria, profile_photo_url, video_url, answers_parsed, photo_urls
    )

@router.get("", response_model=list[PostalListItem])
async def list_postales(db: AsyncSession = Depends(get_db)):
    return await crud.get_postales(db)

@router.get("/feed", response_model=list[FeedItem])
async def get_feed(skip: int = 0, limit: int = 10, db: AsyncSession = Depends(get_db)):
    limit = min(limit, 20)
    return await crud.get_feed_postales(db, skip, limit)

@router.get("/videos", response_model=list[VideoPostalItem])
async def get_video_postales(db: AsyncSession = Depends(get_db)):
    return await crud.get_video_postales(db)

@router.get("/answers-feed", response_model=list[AnswerFeedItem])
async def get_answers_feed(skip: int = 0, limit: int = 10, db: AsyncSession = Depends(get_db)):
    limit = min(limit, 500)
    return await crud.get_answers_feed(db, skip, limit)

@router.get("/stats", response_model=AskStats)
async def get_stats(db: AsyncSession = Depends(get_db)):
    return await crud.get_ask_stats(db)

@router.patch("/answers/{answer_id}", status_code=200)
async def patch_answer(answer_id: int, body: dict, db: AsyncSession = Depends(get_db)):
    text = body.get("answer_text", "").strip()
    if not text:
        raise HTTPException(status_code=422, detail="answer_text required")
    answer = await crud.patch_answer_text(db, answer_id, text)
    if not answer:
        raise HTTPException(status_code=404, detail="Answer not found")
    return {"id": answer.id, "answer_text": answer.answer_text}

@router.post("/answers/{answer_id}/media", response_model=AnswerMediaOut, status_code=201)
async def add_answer_media(
    answer_id: int,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
):
    from app.storage import upload_file
    media_type = "video" if file.content_type and file.content_type.startswith("video/") else "image"
    folder = "answer-videos" if media_type == "video" else "answer-photos"
    url = await upload_file(file, folder)
    media = await crud.add_answer_media(db, answer_id, url, media_type)
    if not media:
        raise HTTPException(status_code=404, detail="Answer not found")
    return media

@router.delete("/answers/{answer_id}/media/{media_id}", status_code=204)
async def delete_answer_media(answer_id: int, media_id: int, db: AsyncSession = Depends(get_db)):
    deleted = await crud.delete_answer_media(db, media_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Media not found")

@router.delete("/answers/{answer_id}", status_code=204)
async def delete_answer(answer_id: int, db: AsyncSession = Depends(get_db)):
    deleted = await crud.delete_answer(db, answer_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Answer not found")

@router.delete("/{postal_id}/photos/{photo_id}", status_code=204)
async def delete_postal_photo(postal_id: int, photo_id: int, db: AsyncSession = Depends(get_db)):
    deleted = await crud.delete_postal_photo(db, photo_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Photo not found")

@router.get("/{postal_id}", response_model=PostalOut)
async def get_postal(postal_id: int, db: AsyncSession = Depends(get_db)):
    postal = await crud.get_postal(db, postal_id)
    if not postal:
        raise HTTPException(status_code=404, detail="Postal not found")
    return postal

@router.delete("/{postal_id}", status_code=204)
async def delete_postal(postal_id: int, db: AsyncSession = Depends(get_db)):
    deleted = await crud.delete_postal(db, postal_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Postal not found")
