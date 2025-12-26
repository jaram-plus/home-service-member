# API 테스트용 Request Body 예시

## 회원가입 플로우

**참고**: 회원가입 후 status는 `unverified`입니다. 이메일 인증이 완료되면 `pending`으로 변경됩니다.

## 1. 회원 등록 (POST /members/register)

### 최소 필수 정보만 있는 경우
```json
{
  "email": "hongildong@example.com",
  "name": "홍길동",
  "generation": 41,
  "rank": "정회원"
}
```

### 기본 정보 + 스킬
```json
{
  "email": "developer@example.com",
  "name": "김개발",
  "generation": 41,
  "rank": "정회원",
  "description": "Full-stack developer interested in FastAPI and React",
  "skills": [
    { "skill_name": "Python" },
    { "skill_name": "FastAPI" },
    { "skill_name": "React" }
  ]
}
```

### 전체 정보 (스킬 + 링크 + 이미지)
```json
{
  "email": "jaram_member@example.com",
  "name": "박자람",
  "generation": 41,
  "rank": "정회원",
  "description": "안녕하세요! JARAM 41기 학술부장입니다. 웹 개발과 클라우드 인프라에 관심이 많습니다.",
  "skills": [
    { "skill_name": "Python" },
    { "skill_name": "FastAPI" },
    { "skill_name": "React" },
    { "skill_name": "Docker" },
    { "skill_name": "AWS" }
  ],
  "links": [
    { "link_type": "github", "url": "https://github.com/jaram-member" },
    { "link_type": "linkedin", "url": "https://linkedin.com/in/jaram-member" },
    { "link_type": "blog", "url": "https://jaram-member.tistory.com" },
    { "link_type": "instagram", "url": "https://instagram.com/jaram.member" }
  ],
  "image_url": "https://example.com/profile-images/jaram-member.jpg"
}
```

### OB 회원 예시
```json
{
  "email": "ob_member@example.com",
  "name": "이OB",
  "generation": 35,
  "rank": "OB",
  "description": "현재 클라우드 회사에서 재직중인 35기 OB입니다.",
  "skills": [
    { "skill_name": "Kubernetes" },
    { "skill_name": "Go" },
    { "skill_name": "System Design" }
  ],
  "links": [
    { "link_type": "github", "url": "https://github.com/ob-member" },
    { "link_type": "linkedin", "url": "https://linkedin.com/in/ob-member" }
  ],
  "image_url": "https://example.com/profile-images/ob-member.jpg"
}
```

### 준OB 회원 예시
```json
{
  "email": "prospective_ob@example.com",
  "name": "준준OB",
  "generation": 40,
  "rank": "준OB",
  "description": "취업 준비중인 40기 준OB입니다. 백엔드 개발 직무를 목표로 하고 있습니다.",
  "skills": [
    { "skill_name": "Java" },
    { "skill_name": "Spring Boot" },
    { "skill_name": "MySQL" }
  ],
  "links": [
    { "link_type": "github", "url": "https://github.com/prospective-ob" },
    { "link_type": "solved_ac", "url": "https://solved.ac/profile/prospective-ob" }
  ]
}
```

### 알고리즘 스터디 회원
```json
{
  "email": "algorithm_master@example.com",
  "name": "알고리즘마스터",
  "generation": 41,
  "rank": "정회원",
  "description": "PS 동아리 활동 중입니다. BOJ 2000 solved",
  "skills": [
    { "skill_name": "C++" },
    { "skill_name": "Python" },
    { "skill_name": "Algorithm" }
  ],
  "links": [
    { "link_type": "github", "url": "https://github.com/algo-master" },
    { "link_type": "solved_ac", "url": "https://solved.ac/profile/algo-master" },
    { "link_type": "notion", "url": "https://notion.site/algo-master/study-log" }
  ]
}
```

---

## 2. 회원 정보 수정 (PUT /members/{member_id})

### 이름만 수정
```json
{
  "name": "홍길동(수정됨)"
}
```

### 스킬만 수정 (기존 스킬 모두 삭제 후 새로 추가)
```json
{
  "skills": [
    { "skill_name": "Python" },
    { "skill_name": "TypeScript" },
    { "skill_name": "Vue.js" }
  ]
}
```

### 링크만 수정
```json
{
  "links": [
    { "link_type": "github", "url": "https://github.com/updated-profile" },
    { "link_type": "blog", "url": "https://new-blog.com" }
  ]
}
```

### 모든 정보 수정
```json
{
  "name": "홍길동",
  "rank": "OB",
  "description": "업데이트된 소개글입니다.",
  "skills": [
    { "skill_name": "Python" },
    { "skill_name": "FastAPI" },
    { "skill_name": "Kubernetes" }
  ],
  "links": [
    { "link_type": "github", "url": "https://github.com/updated" },
    { "link_type": "linkedin", "url": "https://linkedin.com/in/updated" },
    { "link_type": "notion", "url": "https://notion.site/updated" }
  ],
  "image_url": "https://example.com/new-image.jpg"
}
```

---

## cURL 테스트 예시

### 회원 등록
```bash
curl -X POST "http://localhost:8000/members/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "name": "테스트유저",
    "generation": 41,
    "rank": "정회원",
    "description": "테스트 유저입니다",
    "skills": [
      {"skill_name": "Python"},
      {"skill_name": "FastAPI"}
    ],
    "links": [
      {"link_type": "github", "url": "https://github.com/test"}
    ]
  }'
```

### 회원 목록 조회
```bash
curl "http://localhost:8000/members"
```

### 대기중인 회원만 조회
```bash
curl "http://localhost:8000/members?status=pending"
```

### 특정 회원 조회
```bash
curl "http://localhost:8000/members/1"
```

### 회원 정보 수정
```bash
curl -X PUT "http://localhost:8000/members/1" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "수정된 이름",
    "description": "수정된 소개"
  }'
```

### 회원 승인 (관리자)
```bash
curl -X POST "http://localhost:8000/members/1/approve"
```

### 회원 거절 (관리자)
```bash
curl -X POST "http://localhost:8000/members/1/reject"
```

### 회원 삭제 (관리자)
```bash
curl -X DELETE "http://localhost:8000/members/1"
```

---

## 가능한 Rank 값
- `"정회원"` (REGULAR)
- `"OB"`
- `"준OB"` (PROSPECTIVE_OB)

## 가능한 Link Type 값
- `"github"`
- `"linkedin"`
- `"blog"`
- `"instagram"`
- `"notion"`
- `"solved_ac"`
