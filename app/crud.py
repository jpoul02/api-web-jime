# app/crud.py
import random
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, update
from app.models import Question, Postal, Answer, Photo, PopularSong, Album, AlbumTrack, HistoriaSlide, MomentoFavorito, Carta
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
    await reshuffle_answers_feed(db)
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
    stmt = (
        select(Postal)
        .options(selectinload(Postal.photos))
        .order_by(Postal.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    result = await db.execute(stmt)
    return result.scalars().all()

async def get_video_postales(db: AsyncSession) -> list[Postal]:
    result = await db.execute(
        select(Postal)
        .where(Postal.video_url.isnot(None))
        .order_by(Postal.created_at.desc())
    )
    return result.scalars().all()

async def reshuffle_answers_feed(db: AsyncSession) -> None:
    """Assign a new random feed_order to every answer and persist it."""
    result = await db.execute(select(Answer.id))
    ids: list[int] = list(result.scalars().all())
    random.shuffle(ids)
    for order, answer_id in enumerate(ids):
        await db.execute(update(Answer).where(Answer.id == answer_id).values(feed_order=order))
    await db.commit()

async def get_answers_feed(db: AsyncSession, skip: int = 0, limit: int = 10):
    """Flat list of answers with question text + postal author info, for Ask.fm feed."""
    from sqlalchemy.orm import selectinload
    from sqlalchemy import nulls_last
    stmt = (
        select(Answer)
        .options(selectinload(Answer.question), selectinload(Answer.postal))
        .join(Answer.postal)
        .order_by(nulls_last(Answer.feed_order))
        .offset(skip)
        .limit(limit)
    )
    result = await db.execute(stmt)
    rows = result.scalars().all()
    return [
        {
            "id": a.id,
            "question_text": a.question.text,
            "answer_text": a.answer_text,
            "name": a.postal.name,
            "profile_photo_url": a.postal.profile_photo_url,
            "created_at": a.postal.created_at,
        }
        for a in rows
    ]

async def get_ask_stats(db: AsyncSession) -> dict:
    from sqlalchemy import func as sqlfunc
    postales_count = (await db.execute(select(sqlfunc.count()).select_from(Postal))).scalar_one()
    answers_count = (await db.execute(select(sqlfunc.count()).select_from(Answer))).scalar_one()
    return {"total_postales": postales_count, "total_answers": answers_count}

async def delete_postal(db: AsyncSession, postal_id: int) -> bool:
    postal = await db.get(Postal, postal_id)
    if not postal:
        return False
    await db.delete(postal)
    await db.commit()
    return True

async def delete_answer(db: AsyncSession, answer_id: int) -> bool:
    answer = await db.get(Answer, answer_id)
    if not answer:
        return False
    await db.delete(answer)
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

# ── Music ─────────────────────────────────────────────────────────────────────

async def get_popular_songs(db: AsyncSession) -> list[PopularSong]:
    result = await db.execute(select(PopularSong).order_by(PopularSong.order, PopularSong.id))
    return result.scalars().all()

async def create_popular_song(db: AsyncSession, title: str, cover_url: str | None, audio_url: str | None) -> PopularSong:
    count_result = await db.execute(select(func.count()).select_from(PopularSong))
    count = count_result.scalar_one()
    song = PopularSong(title=title, cover_url=cover_url, audio_url=audio_url, order=count)
    db.add(song)
    await db.commit()
    await db.refresh(song)
    return song

async def update_popular_song(db: AsyncSession, song_id: int, title: str | None, cover_url: str | None, audio_url: str | None) -> PopularSong | None:
    song = await db.get(PopularSong, song_id)
    if not song:
        return None
    if title is not None:
        song.title = title
    if cover_url is not None:
        song.cover_url = cover_url
    if audio_url is not None:
        song.audio_url = audio_url
    await db.commit()
    await db.refresh(song)
    return song

async def delete_popular_song(db: AsyncSession, song_id: int) -> bool:
    song = await db.get(PopularSong, song_id)
    if not song:
        return False
    await db.delete(song)
    await db.commit()
    return True

async def reorder_popular_songs(db: AsyncSession, ordered_ids: list[int]) -> list[PopularSong]:
    for i, song_id in enumerate(ordered_ids):
        song = await db.get(PopularSong, song_id)
        if song:
            song.order = i
    await db.commit()
    return await get_popular_songs(db)

async def get_albums(db: AsyncSession) -> list[Album]:
    from sqlalchemy.orm import selectinload
    result = await db.execute(
        select(Album).options(selectinload(Album.tracks)).order_by(Album.order, Album.id)
    )
    return result.scalars().all()

async def create_album(db: AsyncSession, title: str, cover_url: str | None, year: int | None) -> Album:
    from sqlalchemy.orm import selectinload
    count_result = await db.execute(select(func.count()).select_from(Album))
    count = count_result.scalar_one()
    album = Album(title=title, cover_url=cover_url, year=year, order=count)
    db.add(album)
    await db.commit()
    result = await db.execute(select(Album).options(selectinload(Album.tracks)).where(Album.id == album.id))
    return result.scalar_one()

async def update_album(db: AsyncSession, album_id: int, title: str | None, cover_url: str | None, year: int | None) -> Album | None:
    from sqlalchemy.orm import selectinload
    album = await db.get(Album, album_id)
    if not album:
        return None
    if title is not None:
        album.title = title
    if cover_url is not None:
        album.cover_url = cover_url
    if year is not None:
        album.year = year
    await db.commit()
    result = await db.execute(select(Album).options(selectinload(Album.tracks)).where(Album.id == album_id))
    return result.scalar_one()

async def delete_album(db: AsyncSession, album_id: int) -> bool:
    album = await db.get(Album, album_id)
    if not album:
        return False
    await db.delete(album)
    await db.commit()
    return True

async def add_track_to_album(db: AsyncSession, album_id: int, title: str, audio_url: str | None) -> AlbumTrack | None:
    album = await db.get(Album, album_id)
    if not album:
        return None
    count_result = await db.execute(
        select(func.count()).select_from(AlbumTrack).where(AlbumTrack.album_id == album_id)
    )
    count = count_result.scalar_one()
    track = AlbumTrack(album_id=album_id, title=title, audio_url=audio_url, order=count)
    db.add(track)
    await db.commit()
    await db.refresh(track)
    return track

async def update_track(db: AsyncSession, track_id: int, title: str | None, audio_url: str | None) -> AlbumTrack | None:
    track = await db.get(AlbumTrack, track_id)
    if not track:
        return None
    if title is not None:
        track.title = title
    if audio_url is not None:
        track.audio_url = audio_url
    await db.commit()
    await db.refresh(track)
    return track

async def delete_track(db: AsyncSession, track_id: int) -> bool:
    track = await db.get(AlbumTrack, track_id)
    if not track:
        return False
    await db.delete(track)
    await db.commit()
    return True

# ── Historia Slides ───────────────────────────────────────────────────────────

async def get_historia_slides(db: AsyncSession) -> list[HistoriaSlide]:
    result = await db.execute(select(HistoriaSlide).order_by(HistoriaSlide.order))
    return result.scalars().all()

async def create_historia_slide(
    db: AsyncSession,
    date: str,
    title: str,
    desc: str,
    type_: str,
    img_url: str | None,
    emoji: str | None,
) -> HistoriaSlide:
    slides = await get_historia_slides(db)
    slide = HistoriaSlide(
        date=date, title=title, desc=desc, type=type_,
        img_url=img_url, emoji=emoji, order=len(slides),
    )
    db.add(slide)
    await db.commit()
    await db.refresh(slide)
    return slide

async def update_historia_slide(
    db: AsyncSession,
    slide_id: int,
    date: str | None,
    title: str | None,
    desc: str | None,
    type_: str | None,
    img_url: str | None,
    emoji: str | None,
) -> HistoriaSlide | None:
    slide = await db.get(HistoriaSlide, slide_id)
    if not slide:
        return None
    if date is not None:
        slide.date = date
    if title is not None:
        slide.title = title
    if desc is not None:
        slide.desc = desc
    if type_ is not None:
        slide.type = type_
    if img_url is not None:
        slide.img_url = img_url
    if emoji is not None:
        slide.emoji = emoji
    await db.commit()
    await db.refresh(slide)
    return slide

async def delete_historia_slide(db: AsyncSession, slide_id: int) -> bool:
    slide = await db.get(HistoriaSlide, slide_id)
    if not slide:
        return False
    await db.delete(slide)
    await db.commit()
    return True

async def reorder_historia_slides(db: AsyncSession, ids: list[int]) -> list[HistoriaSlide]:
    for i, sid in enumerate(ids):
        slide = await db.get(HistoriaSlide, sid)
        if slide:
            slide.order = i
    await db.commit()
    return await get_historia_slides(db)

# ── Momentos Favoritos ────────────────────────────────────────────────────────

async def get_momentos_favoritos(db: AsyncSession) -> list[MomentoFavorito]:
    result = await db.execute(select(MomentoFavorito).order_by(MomentoFavorito.order))
    return result.scalars().all()

async def create_momento_favorito(db: AsyncSession, photo_url: str) -> MomentoFavorito:
    momentos = await get_momentos_favoritos(db)
    m = MomentoFavorito(photo_url=photo_url, order=len(momentos))
    db.add(m)
    await db.commit()
    await db.refresh(m)
    return m

async def delete_momento_favorito(db: AsyncSession, momento_id: int) -> bool:
    m = await db.get(MomentoFavorito, momento_id)
    if not m:
        return False
    await db.delete(m)
    await db.commit()
    return True

async def reorder_momentos_favoritos(db: AsyncSession, ids: list[int]) -> list[MomentoFavorito]:
    for i, mid in enumerate(ids):
        m = await db.get(MomentoFavorito, mid)
        if m:
            m.order = i
    await db.commit()
    return await get_momentos_favoritos(db)

# ── Carta ─────────────────────────────────────────────────────────────────────

async def get_carta(db: AsyncSession) -> Carta | None:
    return await db.get(Carta, 1)

async def upsert_carta(db: AsyncSession, texto: str) -> Carta:
    carta = await db.get(Carta, 1)
    if carta:
        carta.texto = texto
    else:
        carta = Carta(id=1, texto=texto)
        db.add(carta)
    await db.commit()
    await db.refresh(carta)
    return carta
