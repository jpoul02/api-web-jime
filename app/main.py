# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from contextlib import asynccontextmanager
import os

load_dotenv()

from app.database import engine, async_session_factory, Base
from app.models import Question
from app.routers import questions, postales
from sqlalchemy import text

async def _seed():
    from sqlalchemy import select
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        # Add dedicatoria column to existing deployments that predate the field
        await conn.execute(text(
            "ALTER TABLE postales ADD COLUMN IF NOT EXISTS dedicatoria TEXT"
        ))
    async with async_session_factory() as session:
        result = await session.execute(select(Question))
        if result.scalars().first():
            return
        texts = [
            "¿Cuál es tu recuerdo favorito con Jime?",
            "¿Cómo fue que se conocieron?",
            "¿Qué canción o película te recuerda a ella?",
            "Del 1 al 10, ¿qué tan random es Jimena? (y justificá tu respuesta)",
            "¿Qué cosa rara o peculiar solo Jime haría?",
            "¿Qué es lo que más admiras de Jime?",
            "¿Qué superpoder crees que tiene Jime en la vida real?",
            "Si Jime fuera un personaje de videojuego/película, ¿quién sería y por qué?",
            "¿En qué es Jime mejor que nadie que conozcas?",
            "¿Qué le deseas a Jime para este año?",
            "¿Qué aventura te gustaría vivir con ella que todavía no han hecho?",
            "¿Qué consejo le darías a Jime para esta nueva vuelta al sol?",
            "Del 1 al 10, ¿qué tan buena amiga es Jime? ¿Por qué?",
            "Del 1 al 10, ¿qué tan dramática es Jime? Danos los detalles.",
            "¿Cuál es el meme que más la representa?",
        ]
        for text in texts:
            session.add(Question(text=text))
        await session.commit()

@asynccontextmanager
async def lifespan(app: FastAPI):
    await _seed()
    yield

app = FastAPI(title="jime-api", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "http://localhost:3000").split(","),
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(questions.router)
app.include_router(postales.router)

@app.get("/health")
async def health():
    return {"status": "ok"}
