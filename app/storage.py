import boto3
import os
import uuid
from fastapi import UploadFile

def _get_client():
    return boto3.client(
        "s3",
        endpoint_url=f"https://{os.getenv('R2_ACCOUNT_ID')}.r2.cloudflarestorage.com",
        aws_access_key_id=os.getenv("R2_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("R2_SECRET_ACCESS_KEY"),
        region_name="auto",
    )

async def upload_file(file: UploadFile, folder: str) -> str:
    """Upload a file to R2 and return its public URL."""
    ext = file.filename.rsplit(".", 1)[-1] if "." in file.filename else "bin"
    key = f"{folder}/{uuid.uuid4()}.{ext}"
    contents = await file.read()
    client = _get_client()
    client.put_object(
        Bucket=os.getenv("R2_BUCKET_NAME"),
        Key=key,
        Body=contents,
        ContentType=file.content_type or "application/octet-stream",
    )
    return f"{os.getenv('R2_PUBLIC_URL')}/{key}"
