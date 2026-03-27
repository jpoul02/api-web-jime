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
    postal: Mapped["Postal"] = relationship("Postal", back_populates="answers")
    question: Mapped["Question"] = relationship("Question")

class Photo(Base):
    __tablename__ = "photos"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    postal_id: Mapped[int] = mapped_column(ForeignKey("postales.id"), nullable=False)
    photo_url: Mapped[str] = mapped_column(String, nullable=False)
    order: Mapped[int] = mapped_column(Integer, default=0)
    postal: Mapped["Postal"] = relationship("Postal", back_populates="photos")
