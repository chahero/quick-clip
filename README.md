# quick-clip

`quick-clip` turns local uploads into local URLs for quick sharing and reuse.

## Run

Start the server with one command:

```bash
python main.py
```

`main.py` reads `.env` values automatically:

- `LOCAL_BUCKET_HOST` (default: `127.0.0.1`)
- `LOCAL_BUCKET_PORT` (default: `8000`)
- `LOCAL_BUCKET_DIR` (default: `./bucket`)
- `LOCAL_BUCKET_STATIC` (default: `./static`)
- `LOCAL_BUCKET_ALLOWED_PREFIXES` (default: `image/`)
- `LOCAL_BUCKET_MAX_BYTES` (default: `10485760`)
- `LOCAL_BUCKET_TTL_SECONDS` (default: `0`)
- `LOCAL_BUCKET_MAX_FILES` (default: `0`)
- `LOCAL_BUCKET_RELOAD` (default: `false`)

For reload during local development:

```bash
LOCAL_BUCKET_RELOAD=true
```

## Endpoints

- `POST /upload`: Upload image and receive URL
- `GET /s/{filename}`: Serve image
- `GET /list`: List stored images (supports `?limit=<n>&offset=<n>`)
- `DELETE /s/{filename}`: Delete an image
- `POST /purge`: Remove all stored images
- `GET /health`: Health check

No separate CLI launcher script is required.
