from __future__ import annotations

import mimetypes
import secrets
from pathlib import Path
import os

from fastapi import HTTPException, UploadFile, status

from app.core.config import Settings


def assert_image_file(upload_file: UploadFile, allowed_prefixes: tuple[str, ...]) -> None:
    content_type = upload_file.content_type or ""
    if not any(content_type.startswith(prefix) for prefix in allowed_prefixes):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only image uploads are allowed.",
        )


def normalize_extension(upload_file: UploadFile) -> str:
    original_ext = Path(upload_file.filename or "").suffix.lower()
    if original_ext:
        return original_ext

    guessed = mimetypes.guess_extension(upload_file.content_type or "")
    return guessed or ".png"


def next_filename(bucket_dir: Path, extension: str) -> Path:
    while True:
        token = secrets.token_urlsafe(6)
        candidate = bucket_dir / f"{token}{extension}"
        if not candidate.exists():
            return candidate


def save_upload_file(settings: Settings, upload_file: UploadFile) -> Path:
    assert_image_file(upload_file, settings.allowed_mime_prefixes)

    extension = normalize_extension(upload_file)
    target = next_filename(settings.bucket_dir, extension)

    bytes_copied = 0
    with target.open("wb") as stream:
        while True:
            chunk = upload_file.file.read(8192)
            if not chunk:
                break
            bytes_copied += len(chunk)
            if bytes_copied > settings.max_upload_bytes:
                stream.close()
                target.unlink(missing_ok=True)
                raise HTTPException(
                    status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                    detail=f"Image exceeds max size: {settings.max_upload_bytes} bytes.",
                )
            stream.write(chunk)

    upload_file.file.close()
    os.utime(target, None)
    return target
