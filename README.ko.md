# quick-clip

`quick-clip`은(는) 이미지를 빠르게 업로드하고 클립보드로 공유할 수 있는 웹 기반 툴입니다.  
직접 업로드한 이미지 URL을 즉시 복사하고, 갤러리에서 이미지 관리도 가능합니다.

## 실행 방법

서버를 실행합니다.

```bash
python main.py
```

`main.py`는 `.env` 값을 자동으로 읽습니다.

- `LOCAL_BUCKET_HOST` (기본값: `127.0.0.1`)
- `LOCAL_BUCKET_PORT` (기본값: `8000`)
- `LOCAL_BUCKET_DIR` (기본값: `./bucket`)
- `LOCAL_BUCKET_STATIC` (기본값: `./static`)
- `LOCAL_BUCKET_ALLOWED_PREFIXES` (기본값: `image/`)
- `LOCAL_BUCKET_MAX_BYTES` (기본값: `10485760`)
- `LOCAL_BUCKET_TTL_SECONDS` (기본값: `0`)
- `LOCAL_BUCKET_MAX_FILES` (기본값: `0`)
- `LOCAL_BUCKET_RELOAD` (기본값: `false`)

개발 중 자동 재시작을 사용할 때:

```bash
LOCAL_BUCKET_RELOAD=true
```

## 주요 기능

- 파일 업로드
  - 파일 선택 업로드 및 드래그 앤 드롭 업로드 지원
- 복사
  - 이미지 URL 복사
  - 이미지 데이터(바이너리) 클립보드 복사
- 이미지 미리보기 갤러리
- 최근 업로드
  - 최신 업로드 목록 표시
- 갤러리 관리
  - 페이지네이션(`Load more`)
  - 다중 선택 삭제
  - 다중 선택 삭제 확인 모달
  - 모바일 대응 UI
- 백엔드에 `/purge` 엔드포인트가 있지만, UI 기본 흐름은 다중 선택 삭제 기반입니다.

## API 엔드포인트

- `POST /upload`: 이미지 업로드 후 URL 반환
- `GET /s/{filename}`: 이미지 제공
- `GET /list`: 저장된 이미지 목록 조회 (`?limit=<n>&offset=<n>`)
- `DELETE /s/{filename}`: 단일 이미지 삭제
- `POST /purge`: 전체 이미지 삭제
- `GET /health`: 헬스체크

별도 CLI 실행 스크립트는 필요하지 않습니다.
