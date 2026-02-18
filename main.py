from app.main import app
from app.core.config import get_settings
import uvicorn


def main() -> None:
    settings = get_settings()
    print(f"quick-clip running on http://{settings.host}:{settings.port}")
    uvicorn.run(
        app,
        host=settings.host,
        port=settings.port,
        reload=settings.reload,
    )


if __name__ == '__main__':
    main()
