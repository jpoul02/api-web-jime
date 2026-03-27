# app/routers/questions.py
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app import crud
from app.schemas import QuestionOut

router = APIRouter(prefix="/questions", tags=["questions"])

@router.get("/random", response_model=list[QuestionOut])
async def get_random_questions(
    count: int = Query(default=5, ge=1, le=15),
    exclude: str = Query(default=""),
    db: AsyncSession = Depends(get_db),
):
    exclude_ids = [int(x) for x in exclude.split(",") if x.strip().isdigit()]
    questions = await crud.get_random_questions(db, count=count, exclude=exclude_ids)
    return questions
