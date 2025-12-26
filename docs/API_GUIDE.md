# API 사용 가이드

## 개요
이 API는 JARAM 회원 관리 시스템을 위한 FastAPI 기반 백엔드 서비스입니다.

## 회원가입 및 승인 플로우

1. **회원가입** → `POST /members/register`
   - 사용자가 프로필 정보 입력
   - DB에 저장 (status: `unverified`)
   - 이메일로 Magic Link 발송

2. **이메일 인증** → `GET /auth/verify?token=<token>`
   - 사용자가 Magic Link 클릭
   - 토큰 검증
   - status 변경: `unverified` → `pending`

3. **관리자 승인** → `POST /members/{id}/approve`
   - 관리자가 대시보드에서 승인
   - status 변경: `pending` → `approved`
   - 승인 이메일 발송

4. **거절** → `POST /members/{id}/reject`
   - 관리자가 거절
   - DB에서 완전 삭제

---

## 시작하기

### 1. 의존성 설치
```bash
uv sync
```

### 2. 환경 변수 설정
`.env.example`을 복사하여 `.env` 파일을 생성하고 설정을 수정하세요:
```bash
cp .env.example .env
```

### 3. 데이터베이스 마이그레이션
```bash
# 마이그레이션 생성
uv run alembic revision --autogenerate -m "description"

# 마이그레이션 적용
uv run alembic upgrade head
```

### 4. 서버 실행
```bash
uv run uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 5. API 문서 확인
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## API 엔드포인트

### 1. 회원 등록 (Registration)
```http
POST /members/register
Content-Type: application/json

{
  "email": "test@example.com",
  "name": "홍길동",
  "generation": 41,
  "rank": "정회원",
  "description": "안녕하세요",
  "skills": [
    {"skill_name": "Python"},
    {"skill_name": "FastAPI"}
  ],
  "links": [
    {"link_type": "github", "url": "https://github.com/user"}
  ],
  "image_url": "https://example.com/image.jpg"
}
```

### 2. 매직 링크 인증 요청
```http
POST /auth/magic-link/register
Content-Type: application/json

{
  "email": "test@example.com"
}
```

### 3. 매직 링크 확인
```http
GET /auth/verify?token=<jwt_token>
```

### 4. 회원 목록 조회
```http
GET /members
GET /members?status=pending
```

### 5. 특정 회원 조회
```http
GET /members/{member_id}
```

### 6. 회원 정보 수정
```http
PUT /members/{member_id}
Content-Type: application/json

{
  "name": "홍길동",
  "rank": "OB",
  "description": "수정된 소개"
}
```

**참고**: 현재는 인증 없이 누구나 수정 가능합니다. 추후 JWT 토큰을 통한 인증이 추가될 예정입니다.

### 7. 회원 승인 (관리자)
```http
POST /members/{member_id}/approve
```

### 8. 회원 거절 (관리자)
```http
POST /members/{member_id}/reject
```

### 9. 회원 삭제 (관리자)
```http
DELETE /members/{member_id}
```

## 회원 등급 (Rank)
- `정회원` (REGULAR)
- `OB`
- `준OB` (PROSPECTIVE_OB)

## 회원 상태 (Status)
- `unverified`: 이메일 인증 전 (회원가입 직후 상태)
- `pending`: 이메일 인증 완료, 관리자 승인 대기
- `approved`: 관리자 승인 완료

## 링크 타입 (Link Type)
- `github`
- `linkedin`
- `blog`
- `instagram`
- `notion`
- `solved_ac`

## 이메일 서비스 구현
현재 `MockEmailService`가 구현되어 있어 로그에 이메일 내용이 출력됩니다.

실제 이메일 발송을 위해서는:
1. `services/email_service_impl.py`에서 `MockEmailService`를 실제 구현체로 교체
2. AWS SES, SendGrid, Mailgun 등의 API를 사용하여 구현
3. `.env` 파일에 API 키 설정

## 테스트
```bash
uv run pytest
```

## Linting & Formatting
```bash
# Lint check
uv run ruff check .

# Format code
uv run ruff format .

# Type check
uv run mypy .
```
