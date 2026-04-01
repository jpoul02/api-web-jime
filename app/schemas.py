# app/schemas.py
from pydantic import BaseModel
from datetime import datetime

class QuestionOut(BaseModel):
    id: int
    text: str
    model_config = {"from_attributes": True}

class AnswerIn(BaseModel):
    question_id: int
    answer_text: str

class PhotoOut(BaseModel):
    id: int
    photo_url: str
    order: int
    model_config = {"from_attributes": True}

class AnswerOut(BaseModel):
    id: int
    question_id: int
    answer_text: str
    question: QuestionOut
    model_config = {"from_attributes": True}

class PostalOut(BaseModel):
    id: int
    name: str
    dedicatoria: str | None = None
    profile_photo_url: str | None
    video_url: str | None
    created_at: datetime
    answers: list[AnswerOut] = []
    photos: list[PhotoOut] = []
    model_config = {"from_attributes": True}

class PostalListItem(BaseModel):
    id: int
    name: str
    dedicatoria: str | None = None
    profile_photo_url: str | None
    created_at: datetime
    model_config = {"from_attributes": True}

class FeedPhotoItem(BaseModel):
    id: int
    photo_url: str
    model_config = {"from_attributes": True}

class FeedItem(BaseModel):
    id: int
    name: str
    dedicatoria: str | None = None
    profile_photo_url: str | None
    created_at: datetime
    photos: list[FeedPhotoItem] = []
    model_config = {"from_attributes": True}

# ── Music ────────────────────────────────────────────────────────────────────

class PopularSongOut(BaseModel):
    id: int
    title: str
    cover_url: str | None = None
    audio_url: str | None = None
    order: int
    model_config = {"from_attributes": True}

class AlbumTrackOut(BaseModel):
    id: int
    title: str
    audio_url: str | None = None
    order: int
    model_config = {"from_attributes": True}

class AlbumOut(BaseModel):
    id: int
    title: str
    cover_url: str | None = None
    year: int | None = None
    order: int
    tracks: list[AlbumTrackOut] = []
    model_config = {"from_attributes": True}
