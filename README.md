# home-service-member

JARAM member management service built with FastAPI.

## TODO

- [ ] **프로필 수정 인증 구현**: Magic Link 인증 후에만 본인 프로필 수정 가능하도록 구현
  - `PUT /members/{member_id}` 엔드포인트 현재 비활성화됨
  - Ref: `home-docs/docs-meeting/251220-project-specification-meeting-note.md`
  - Sequence: 이메일 인증 → Magic Link → 토큰 검증 → 수정 권한 확인 → 업데이트

## Development Setup

```bash
# Install dependencies
uv sync

# Run development server
uv run uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Run tests
uv run pytest

# Lint and format
uv run ruff check .
uv run ruff format .
```

## Docker Setup

```bash
# Start all services
docker-compose up -d

# MinIO 초기 설정 (버킷 생성 및 공개 접근 허용)
docker exec minio mc alias set local http://localhost:9000 minioadmin minioadmin
docker exec minio mc mb local/profiles
docker exec minio mc anonymous set download local/profiles
```

## Project Structure

```
├── main.py                      # FastAPI app entry point
├── database.py                  # DB connection setup
├── config.py                    # Environment variables and configuration
├── models/                      # ORM models
├── schemas/                     # Pydantic schemas
├── repositories/                # Database queries
├── services/                    # Business logic
├── routers/                     # API endpoints
└── utils/                       # Utilities
```
