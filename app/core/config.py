from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import os
from functools import lru_cache

from dotenv import load_dotenv


load_dotenv()


@dataclass(frozen=True)
class Settings:
    root_dir: Path
    bucket_dir: Path
    static_dir: Path
    route_prefix: str = "s"
    allowed_mime_prefixes: tuple[str, ...] = ("image/",)
    max_upload_bytes: int = 10 * 1024 * 1024
    retention_seconds: int = 0
    max_files: int = 0
    host: str = "127.0.0.1"
    port: int = 8000
    reload: bool = False


def _env_int(name: str, default: int) -> int:
    value = os.getenv(name)
    if value is None:
        return default
    try:
        return int(value)
    except ValueError as exc:
        raise ValueError(f"Environment variable {name} must be integer.") from exc


def _env_bool(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "t", "yes", "y", "on"}


def _parse_prefixes(raw: str) -> tuple[str, ...]:
    prefixes = tuple(token.strip() for token in raw.split(","))
    return tuple(prefix for prefix in prefixes if prefix)


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    root_dir = Path(__file__).resolve().parents[1]
    bucket_dir = Path(os.getenv("LOCAL_BUCKET_DIR", root_dir / "bucket"))
    static_dir = Path(os.getenv("LOCAL_BUCKET_STATIC", root_dir / "static"))
    allowed = _parse_prefixes(os.getenv("LOCAL_BUCKET_ALLOWED_PREFIXES", "image/"))
    if not allowed:
        allowed = ("image/",)

    bucket_dir.mkdir(parents=True, exist_ok=True)
    static_dir.mkdir(parents=True, exist_ok=True)

    return Settings(
        root_dir=root_dir,
        bucket_dir=bucket_dir,
        static_dir=static_dir,
        allowed_mime_prefixes=allowed,
        max_upload_bytes=_env_int("LOCAL_BUCKET_MAX_BYTES", 10 * 1024 * 1024),
        retention_seconds=_env_int("LOCAL_BUCKET_TTL_SECONDS", 0),
        max_files=_env_int("LOCAL_BUCKET_MAX_FILES", 0),
        host=os.getenv("LOCAL_BUCKET_HOST", "127.0.0.1"),
        port=_env_int("LOCAL_BUCKET_PORT", 8000),
        reload=_env_bool("LOCAL_BUCKET_RELOAD", False),
    )
