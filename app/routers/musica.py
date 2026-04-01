# app/routers/musica.py
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app import crud
from app.schemas import PopularSongOut, AlbumOut, AlbumTrackOut
from app.storage import upload_file, upload_audio, upload_audio_bytes
import asyncio
import tempfile
import os

router = APIRouter(prefix="/musica", tags=["musica"])

MAX_POPULAR = 10

# ── Popular Songs ─────────────────────────────────────────────────────────────

@router.get("/popular", response_model=list[PopularSongOut])
async def list_popular(db: AsyncSession = Depends(get_db)):
    return await crud.get_popular_songs(db)

@router.post("/popular", response_model=PopularSongOut)
async def create_popular(
    title: str = Form(...),
    cover: UploadFile | None = File(None),
    audio: UploadFile | None = File(None),
    youtube_url: str | None = Form(None),
    db: AsyncSession = Depends(get_db),
):
    songs = await crud.get_popular_songs(db)
    if len(songs) >= MAX_POPULAR:
        raise HTTPException(400, f"Máximo {MAX_POPULAR} canciones populares")

    cover_url = await upload_file(cover, "music/covers") if cover else None
    audio_url = None

    if audio:
        audio_url = await upload_audio(audio, "music/audio")
    elif youtube_url:
        audio_url = await _download_youtube(youtube_url)

    return await crud.create_popular_song(db, title, cover_url, audio_url)

@router.patch("/popular/{song_id}", response_model=PopularSongOut)
async def update_popular(
    song_id: int,
    title: str | None = Form(None),
    cover: UploadFile | None = File(None),
    audio: UploadFile | None = File(None),
    youtube_url: str | None = Form(None),
    db: AsyncSession = Depends(get_db),
):
    cover_url = await upload_file(cover, "music/covers") if cover else None
    audio_url = None
    if audio:
        audio_url = await upload_audio(audio, "music/audio")
    elif youtube_url:
        audio_url = await _download_youtube(youtube_url)

    song = await crud.update_popular_song(db, song_id, title, cover_url, audio_url)
    if not song:
        raise HTTPException(404, "Canción no encontrada")
    return song

@router.delete("/popular/{song_id}")
async def delete_popular(song_id: int, db: AsyncSession = Depends(get_db)):
    ok = await crud.delete_popular_song(db, song_id)
    if not ok:
        raise HTTPException(404, "Canción no encontrada")
    return {"ok": True}

@router.post("/popular/reorder")
async def reorder_popular(ids: list[int], db: AsyncSession = Depends(get_db)):
    songs = await crud.reorder_popular_songs(db, ids)
    return songs

# ── Albums ────────────────────────────────────────────────────────────────────

@router.get("/albums", response_model=list[AlbumOut])
async def list_albums(db: AsyncSession = Depends(get_db)):
    return await crud.get_albums(db)

@router.post("/albums", response_model=AlbumOut)
async def create_album(
    title: str = Form(...),
    year: int | None = Form(None),
    cover: UploadFile | None = File(None),
    db: AsyncSession = Depends(get_db),
):
    cover_url = await upload_file(cover, "music/covers") if cover else None
    return await crud.create_album(db, title, cover_url, year)

@router.patch("/albums/{album_id}", response_model=AlbumOut)
async def update_album(
    album_id: int,
    title: str | None = Form(None),
    year: int | None = Form(None),
    cover: UploadFile | None = File(None),
    db: AsyncSession = Depends(get_db),
):
    cover_url = await upload_file(cover, "music/covers") if cover else None
    album = await crud.update_album(db, album_id, title, cover_url, year)
    if not album:
        raise HTTPException(404, "Álbum no encontrado")
    return album

@router.delete("/albums/{album_id}")
async def delete_album(album_id: int, db: AsyncSession = Depends(get_db)):
    ok = await crud.delete_album(db, album_id)
    if not ok:
        raise HTTPException(404, "Álbum no encontrado")
    return {"ok": True}

# ── Album Tracks ──────────────────────────────────────────────────────────────

@router.post("/albums/{album_id}/tracks", response_model=AlbumTrackOut)
async def add_track(
    album_id: int,
    title: str = Form(...),
    audio: UploadFile | None = File(None),
    youtube_url: str | None = Form(None),
    db: AsyncSession = Depends(get_db),
):
    audio_url = None
    if audio:
        audio_url = await upload_audio(audio, "music/audio")
    elif youtube_url:
        audio_url = await _download_youtube(youtube_url)

    track = await crud.add_track_to_album(db, album_id, title, audio_url)
    if not track:
        raise HTTPException(404, "Álbum no encontrado")
    return track

@router.patch("/tracks/{track_id}", response_model=AlbumTrackOut)
async def update_track(
    track_id: int,
    title: str | None = Form(None),
    audio: UploadFile | None = File(None),
    youtube_url: str | None = Form(None),
    db: AsyncSession = Depends(get_db),
):
    audio_url = None
    if audio:
        audio_url = await upload_audio(audio, "music/audio")
    elif youtube_url:
        audio_url = await _download_youtube(youtube_url)

    track = await crud.update_track(db, track_id, title, audio_url)
    if not track:
        raise HTTPException(404, "Track no encontrado")
    return track

@router.delete("/tracks/{track_id}")
async def delete_track(track_id: int, db: AsyncSession = Depends(get_db)):
    ok = await crud.delete_track(db, track_id)
    if not ok:
        raise HTTPException(404, "Track no encontrado")
    return {"ok": True}

# ── YouTube Download ──────────────────────────────────────────────────────────

async def _download_youtube(url: str) -> str:
    """Download audio from YouTube URL and upload to Cloudinary. Returns audio URL."""
    import yt_dlp

    with tempfile.TemporaryDirectory() as tmp:
        out_path = os.path.join(tmp, "audio.%(ext)s")
        # Prefer m4a (native, no FFmpeg needed), fallback to any bestaudio
        ydl_opts = {
            "format": "bestaudio[ext=m4a]/bestaudio/best",
            "outtmpl": out_path,
            "quiet": True,
            "no_warnings": True,
        }

        def _run():
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            files = os.listdir(tmp)
            if not files:
                raise RuntimeError("yt-dlp no generó archivo de audio")
            return os.path.join(tmp, files[0])

        audio_path = await asyncio.to_thread(_run)
        with open(audio_path, "rb") as f:
            data = f.read()

    return await upload_audio_bytes(data, "music/audio")
