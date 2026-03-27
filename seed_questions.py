# seed_questions.py
import asyncio
from app.database import engine, async_session_factory, Base
from app.models import Question

QUESTIONS = [
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

async def seed():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async with async_session_factory() as session:
        from sqlalchemy import select
        result = await session.execute(select(Question))
        if result.scalars().first():
            print("Questions already seeded.")
            return
        for text in QUESTIONS:
            session.add(Question(text=text))
        await session.commit()
        print(f"Seeded {len(QUESTIONS)} questions.")

if __name__ == "__main__":
    asyncio.run(seed())
