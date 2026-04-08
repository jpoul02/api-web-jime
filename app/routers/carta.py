# app/routers/carta.py
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app import crud
from app.schemas import CartaIn, CartaOut

router = APIRouter(prefix="/carta", tags=["carta"])

@router.get("", response_model=CartaOut)
async def get_carta(db: AsyncSession = Depends(get_db)):
    carta = await crud.get_carta(db)
    return CartaOut(texto=carta.texto if carta else None)

@router.put("", response_model=CartaOut)
async def update_carta(body: CartaIn, db: AsyncSession = Depends(get_db)):
    carta = await crud.upsert_carta(db, body.texto)
    return CartaOut(texto=carta.texto)
