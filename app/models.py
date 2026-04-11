# app/models.py
from sqlalchemy import Integer, String, ForeignKey, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base
from datetime import datetime

class Question(Base):
    __tablename__ = "questions"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    text: Mapped[str] = mapped_column(String, nullable=False)

class Postal(Base):
    __tablename__ = "postales"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    dedicatoria: Mapped[str | None] = mapped_column(String, nullable=True)
    profile_photo_url: Mapped[str | None] = mapped_column(String, nullable=True)
    video_url: Mapped[str | None] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    answers: Mapped[list["Answer"]] = relationship("Answer", back_populates="postal", cascade="all, delete")
    photos: Mapped[list["Photo"]] = relationship("Photo", back_populates="postal", cascade="all, delete", order_by="Photo.order")

class Answer(Base):
    __tablename__ = "answers"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    postal_id: Mapped[int] = mapped_column(ForeignKey("postales.id"), nullable=False)
    question_id: Mapped[int] = mapped_column(ForeignKey("questions.id"), nullable=False)
    answer_text: Mapped[str] = mapped_column(String, nullable=False)
    feed_order: Mapped[int | None] = mapped_column(Integer, nullable=True, index=True)
    postal: Mapped["Postal"] = relationship("Postal", back_populates="answers")
    question: Mapped["Question"] = relationship("Question")
    media: Mapped[list["AnswerMedia"]] = relationship("AnswerMedia", back_populates="answer", cascade="all, delete", order_by="AnswerMedia.order")

class AnswerMedia(Base):
    __tablename__ = "answer_media"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    answer_id: Mapped[int] = mapped_column(ForeignKey("answers.id"), nullable=False)
    media_url: Mapped[str] = mapped_column(String, nullable=False)
    media_type: Mapped[str] = mapped_column(String(10), nullable=False, default="image")  # "image" | "video"
    order: Mapped[int] = mapped_column(Integer, default=0)
    answer: Mapped["Answer"] = relationship("Answer", back_populates="media")

class Photo(Base):
    __tablename__ = "photos"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    postal_id: Mapped[int] = mapped_column(ForeignKey("postales.id"), nullable=False)
    photo_url: Mapped[str] = mapped_column(String, nullable=False)
    order: Mapped[int] = mapped_column(Integer, default=0)
    postal: Mapped["Postal"] = relationship("Postal", back_populates="photos")

class PopularSong(Base):
    __tablename__ = "popular_songs"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    cover_url: Mapped[str | None] = mapped_column(String, nullable=True)
    audio_url: Mapped[str | None] = mapped_column(String, nullable=True)
    order: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

class Album(Base):
    __tablename__ = "albums"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    cover_url: Mapped[str | None] = mapped_column(String, nullable=True)
    year: Mapped[int | None] = mapped_column(Integer, nullable=True)
    order: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    tracks: Mapped[list["AlbumTrack"]] = relationship("AlbumTrack", back_populates="album", cascade="all, delete", order_by="AlbumTrack.order")

class AlbumTrack(Base):
    __tablename__ = "album_tracks"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    album_id: Mapped[int] = mapped_column(ForeignKey("albums.id"), nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    audio_url: Mapped[str | None] = mapped_column(String, nullable=True)
    order: Mapped[int] = mapped_column(Integer, default=0)
    album: Mapped["Album"] = relationship("Album", back_populates="tracks")

class HistoriaSlide(Base):
    __tablename__ = "historia_slides"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    date: Mapped[str] = mapped_column(String(80), nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    desc: Mapped[str] = mapped_column(String, nullable=False)
    type: Mapped[str] = mapped_column(String(20), nullable=False)   # "text" | "arch" | "fullbleed"
    img_url: Mapped[str | None] = mapped_column(String, nullable=True)
    emoji: Mapped[str | None] = mapped_column(String(20), nullable=True)
    order: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

class MomentoFavorito(Base):
    __tablename__ = "momentos_favoritos"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    photo_url: Mapped[str] = mapped_column(String, nullable=False)
    order: Mapped[int] = mapped_column(Integer, default=0)

class Carta(Base):
    __tablename__ = "carta"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, default=1)
    texto: Mapped[str | None] = mapped_column(String, nullable=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )
