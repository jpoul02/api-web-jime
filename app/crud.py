# app/crud.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.models import Question, Postal, Answer, Photo
from app.schemas import AnswerIn

async def get_random_questions(db: AsyncSession, count: int, exclude: list[int]) -> list[Question]:
    stmt = select(Question)
    if exclude:
        stmt = stmt.where(Question.id.notin_(exclude))
    stmt = stmt.order_by(func.random()).limit(count)
    result = await db.execute(stmt)
    return result.scalars().all()
