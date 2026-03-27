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
    """Upload a file to Cloudinary and return its secure URL."""
    contents = await file.read()
    public_id = f"{folder}/{uuid.uuid4()}"
    result = cloudinary.uploader.upload(
        contents,
        public_id=public_id,
        resource_type="auto",
    )
    return result["secure_url"]
