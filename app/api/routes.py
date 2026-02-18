from __future__ import annotations

from pathlib import Path
from time import time

from fastapi import APIRouter, File, HTTPException, Request, UploadFile
from fastapi.responses import FileResponse
import mimetypes

from app.core.config import get_settings
from app.services.cleanup import cleanup_bucket
from app.services.storage import save_upload_file


router = APIRouter()


@router.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/")
def home() -> FileResponse:
    static_index = get_settings().static_dir / "index.html"
    if not static_index.exists():
        raise HTTPException(status_code=404, detail="Frontend not found.")
    return FileResponse(static_index)


@router.post("/upload")
async def upload_image(request: Request, file: UploadFile = File(...)) -> dict[str, str]:
    settings = get_settings()
    cleanup_bucket(settings)
    saved = save_upload_file(settings, file)
    cleanup_bucket(settings)
    return {
        "url": f"{request.base_url}{settings.route_prefix}/{saved.name}",
        "filename": saved.name,
    }


@router.get("/list")
def list_images(
    request: Request, limit: int = 50, offset: int = 0
) -> dict[str, object]:
    settings = get_settings()
    now = time()
    normalized_limit = max(1, min(limit, 200))
    normalized_offset = max(0, offset)

    sorted_files = sorted(
        (path for path in settings.bucket_dir.iterdir() if path.is_file()),
        key=lambda path: path.stat().st_mtime,
        reverse=True,
    )
    total_files = len(sorted_files)

    items = []

    for file_path in sorted_files[normalized_offset : normalized_offset + normalized_limit]:
        stats = file_path.stat()
        created_ts = int(stats.st_mtime)
        ttl_remaining = 0
        if settings.retention_seconds > 0:
            ttl_remaining = max(int(settings.retention_seconds - (now - created_ts)), 0)

        items.append(
            {
                "filename": file_path.name,
                "url": f"{request.base_url}{settings.route_prefix}/{file_path.name}",
                "thumbnail_url": f"{request.base_url}{settings.route_prefix}/{file_path.name}",
                "size_bytes": stats.st_size,
                "created_at": created_ts,
                "ttl_seconds_remaining": ttl_remaining
                if settings.retention_seconds > 0
                else None,
            }
        )

    next_offset = normalized_offset + len(items)
    has_more = next_offset < total_files

    return {
        "items": items,
        "count": len(items),
        "total": total_files,
        "limit": normalized_limit,
        "offset": normalized_offset,
        "next_offset": next_offset,
        "has_more": has_more,
    }


@router.get("/s/{filename}")
def serve_image(filename: str) -> FileResponse:
    settings = get_settings()
    safe_name = Path(filename).name
    file_path = settings.bucket_dir / safe_name

    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Image not found.")

    media_type, _ = mimetypes.guess_type(str(file_path))
    return FileResponse(file_path, media_type=media_type)


@router.delete("/s/{filename}")
def delete_image(filename: str) -> dict[str, str]:
    settings = get_settings()
    safe_name = Path(filename).name
    file_path = settings.bucket_dir / safe_name

    if not file_path.exists() or not file_path.is_file():
        raise HTTPException(status_code=404, detail="Image not found.")

    file_path.unlink(missing_ok=True)
    return {"status": "deleted", "filename": safe_name}


@router.post("/purge")
def purge_bucket() -> dict[str, int]:
    settings = get_settings()
    files = [item for item in settings.bucket_dir.iterdir() if item.is_file()]
    removed = 0
    for file_path in files:
        file_path.unlink(missing_ok=True)
        removed += 1
    cleanup_bucket(settings)
    return {"purged_count": removed}
