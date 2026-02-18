from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager

from app.api.routes import router
from app.core.config import get_settings
from app.services.cleanup import cleanup_bucket


@asynccontextmanager
async def lifespan(_: FastAPI):
    settings = get_settings()
    cleanup_bucket(settings)
    yield


def create_app() -> FastAPI:
    settings = get_settings()

    app = FastAPI(title="quick-clip", lifespan=lifespan)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.mount("/static", StaticFiles(directory=str(settings.static_dir)), name="static")
    app.include_router(router)
    return app


app = create_app()
