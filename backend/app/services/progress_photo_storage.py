import base64
import binascii
import logging
from io import BytesIO
from uuid import uuid4

from fastapi import HTTPException
from PIL import Image, UnidentifiedImageError

from ..config import settings
from ..database import get_supabase

logger = logging.getLogger(__name__)

_FORMAT_TO_MIME = {
    "JPEG": "image/jpeg",
    "PNG": "image/png",
    "WEBP": "image/webp",
}

_FORMAT_TO_EXTENSION = {
    "JPEG": "jpg",
    "PNG": "png",
    "WEBP": "webp",
}


def _decode_progress_photo(image_base64: str) -> tuple[bytes, str, str]:
    if not image_base64 or not image_base64.strip():
        raise HTTPException(status_code=400, detail="Image is required")

    payload = image_base64.strip()
    if payload.startswith("data:") and "," in payload:
        payload = payload.split(",", 1)[1]

    try:
        image_bytes = base64.b64decode(payload, validate=True)
    except (ValueError, binascii.Error) as exc:
        raise HTTPException(status_code=400, detail="Invalid image data") from exc

    if not image_bytes:
        raise HTTPException(status_code=400, detail="Invalid image data")

    if len(image_bytes) > settings.max_upload_bytes:
        raise HTTPException(status_code=413, detail="Image exceeds upload size limit")

    try:
        with Image.open(BytesIO(image_bytes)) as image:
            image_format = (image.format or "JPEG").upper()
    except UnidentifiedImageError as exc:
        raise HTTPException(status_code=400, detail="Unsupported image format") from exc

    mime_type = _FORMAT_TO_MIME.get(image_format, "image/jpeg")
    extension = _FORMAT_TO_EXTENSION.get(image_format, "jpg")
    return image_bytes, mime_type, extension


def upload_progress_image(user_id: str, image_base64: str) -> dict[str, str]:
    image_bytes, mime_type, extension = _decode_progress_photo(image_base64)
    storage_key = f"{user_id}/{uuid4()}.{extension}"

    supabase = get_supabase()
    bucket = supabase.storage.from_(settings.progress_photo_storage_bucket)
    bucket.upload(storage_key, image_bytes, {"content-type": mime_type})

    return {
        "storage_bucket": settings.progress_photo_storage_bucket,
        "storage_key": storage_key,
    }


def build_progress_photo_url(storage_key: str, storage_bucket: str | None = None) -> str:
    if not storage_key:
        raise ValueError("storage_key is required")

    bucket_name = storage_bucket or settings.progress_photo_storage_bucket
    supabase = get_supabase()
    signed = supabase.storage.from_(bucket_name).create_signed_url(
        storage_key,
        settings.progress_photo_signed_url_ttl_seconds,
    )

    url = signed.get("signedURL") or signed.get("signedUrl")
    if not url:
        raise RuntimeError(f"Failed to create signed URL for {storage_key}")
    return url


def delete_progress_image(storage_key: str, storage_bucket: str | None = None) -> None:
    if not storage_key:
        return

    bucket_name = storage_bucket or settings.progress_photo_storage_bucket
    supabase = get_supabase()
    try:
        supabase.storage.from_(bucket_name).remove([storage_key])
    except Exception as exc:
        logger.warning("Failed to delete progress photo object %s: %s", storage_key, exc)
        raise
