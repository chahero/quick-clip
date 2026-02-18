from __future__ import annotations

import os
from pathlib import Path
from time import time

from app.core.config import Settings


def cleanup_bucket(settings: Settings) -> None:
    files = [path for path in settings.bucket_dir.iterdir() if path.is_file()]
    if not files:
        return

    now = time()
    if settings.retention_seconds > 0:
        for path in files:
            age = now - path.stat().st_mtime
            if age > settings.retention_seconds:
                path.unlink(missing_ok=True)

    files = [path for path in settings.bucket_dir.iterdir() if path.is_file()]
    if settings.max_files <= 0 or len(files) <= settings.max_files:
        return

    files.sort(key=lambda item: item.stat().st_mtime)
    overflow = len(files) - settings.max_files
    for path in files[:overflow]:
        path.unlink(missing_ok=True)
