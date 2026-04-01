import asyncio
import cloudinary
import cloudinary.uploader
import os
import uuid
from fastapi import UploadFile

cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET"),
)

async def upload_file(file: UploadFile, folder: str) -> str:
    """Upload a file to Cloudinary without blocking the event loop."""
    contents = await file.read()
    public_id = f"{folder}/{uuid.uuid4()}"
    result = await asyncio.to_thread(
        cloudinary.uploader.upload,
        contents,
        public_id=public_id,
        resource_type="auto",
    )
    return result["secure_url"]

async def maybe_upload(file: UploadFile | None, folder: str) -> str | None:
    if file is None:
        return None
    return await upload_file(file, folder)

async def upload_audio(file: UploadFile, folder: str) -> str:
    """Upload an audio file to Cloudinary using resource_type='video'."""
    contents = await file.read()
    public_id = f"{folder}/{uuid.uuid4()}"
    result = await asyncio.to_thread(
        cloudinary.uploader.upload,
        contents,
        public_id=public_id,
        resource_type="video",
    )
    return result["secure_url"]

async def upload_audio_bytes(data: bytes, folder: str, filename: str) -> str:
    """Upload raw audio bytes (e.g. from yt-dlp) to Cloudinary."""
    public_id = f"{folder}/{uuid.uuid4()}"
    result = await asyncio.to_thread(
        cloudinary.uploader.upload,
        data,
        public_id=public_id,
        resource_type="video",
    )
    return result["secure_url"]
