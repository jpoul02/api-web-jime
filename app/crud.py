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

async def create_postal(
    db: AsyncSession,
    name: str,
    dedicatoria: str | None,
    profile_photo_url: str | None,
    video_url: str | None,
    answers: list[AnswerIn],
    photo_urls: list[str],
) -> Postal:
    from sqlalchemy.orm import selectinload
    postal = Postal(name=name, dedicatoria=dedicatoria, profile_photo_url=profile_photo_url, video_url=video_url)
    db.add(postal)
    await db.flush()
    for ans in answers:
        db.add(Answer(postal_id=postal.id, question_id=ans.question_id, answer_text=ans.answer_text))
    for i, url in enumerate(photo_urls):
        db.add(Photo(postal_id=postal.id, photo_url=url, order=i))
    await db.commit()
    # Re-fetch with eager loading to avoid lazy-load greenlet errors
    result = await db.execute(
        select(Postal)
        .options(selectinload(Postal.answers).selectinload(Answer.question), selectinload(Postal.photos))
        .where(Postal.id == postal.id)
    )
    return result.scalar_one()

async def get_postales(db: AsyncSession) -> list[Postal]:
    from sqlalchemy.orm import selectinload
    result = await db.execute(
        select(Postal).options(selectinload(Postal.photos)).order_by(Postal.created_at.desc())
    )
    return result.scalars().all()

async def get_feed_postales(db: AsyncSession, skip: int = 0, limit: int = 10) -> list[Postal]:
    from sqlalchemy.orm import selectinload
    from sqlalchemy import exists
    stmt = (
        select(Postal)
        .options(selectinload(Postal.photos))
        .where(exists().where(Photo.postal_id == Postal.id))
        .order_by(Postal.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    result = await db.execute(stmt)
    return result.scalars().all()

async def delete_postal(db: AsyncSession, postal_id: int) -> bool:
    postal = await db.get(Postal, postal_id)
    if not postal:
        return False
    await db.delete(postal)
    await db.commit()
    return True

async def get_postal(db: AsyncSession, postal_id: int) -> Postal | None:
    from sqlalchemy.orm import selectinload
    result = await db.execute(
        select(Postal)
        .options(selectinload(Postal.answers).selectinload(Answer.question), selectinload(Postal.photos))
        .where(Postal.id == postal_id)
    )
    return result.scalar_one_or_none()
