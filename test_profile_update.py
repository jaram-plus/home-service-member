"""Test script for profile update functionality."""

import os
import requests
import json

API_BASE = "http://localhost:8000"
REQUEST_TIMEOUT = 10  # seconds

print("=" * 60)
print("프로필 수정 기능 테스트")
print("=" * 60)

# Step 1: Create a test member (if not exists)
print("\n1. 테스트 회원 생성...")
register_data = {
    "email": "test@example.com",
    "name": "테스트 사용자",
    "generation": 1,
    "rank": "정회원",
    "description": "초기 자기소개입니다",
    "image_url": "https://example.com/old-image.jpg",
    "skills": [{"skill_name": "Python"}, {"skill_name": "JavaScript"}],
    "links": [
        {"link_type": "github", "url": "https://github.com/olduser"}
    ]
}

try:
    response = requests.post(
        f"{API_BASE}/members/register",
        json=register_data,
        timeout=REQUEST_TIMEOUT
    )
    if response.status_code == 400:
        print("   ℹ️  회원 이미 존재함 (계속 진행)")
    else:
        response.raise_for_status()
        member = response.json()
        print(f"   ✅ 회원 생성 성공 (ID: {member['id']}, Status: {member['status']})")
except Exception as e:
    print(f"   ⚠️  회원 생성 실패: {e}")

# Step 2: Get member ID
print("\n2. 회원 정보 조회...")
try:
    response = requests.get(
        f"{API_BASE}/members",
        params={"status": "PENDING"},
        timeout=REQUEST_TIMEOUT
    )
    response.raise_for_status()
    members = response.json()

    # Find our test member
    test_member = None
    for m in members:
        if m['email'] == 'test@example.com':
            test_member = m
            break

    if not test_member:
        # Try without status filter
        response = requests.get(
            f"{API_BASE}/members",
            timeout=REQUEST_TIMEOUT
        )
        response.raise_for_status()
        members = response.json()
        for m in members:
            if m['email'] == 'test@example.com':
                test_member = m
                break

    if test_member:
        print(f"   ✅ 회원 찾음 (ID: {test_member['id']}, Status: {test_member['status']})")
        member_id = test_member['id']
    else:
        print("   ❌ 테스트 회원을 찾을 수 없음")
        exit(1)
except Exception as e:
    print(f"   ❌ 회원 조회 실패: {e}")
    exit(1)

# Step 3: Approve the member (if not already APPROVED)
print("\n3. 회원 승인 (APPROVED 상태로 변경)...")
if test_member['status'] != 'APPROVED':
    try:
        # Use admin key to approve (from environment variable for security)
        admin_key = os.environ.get('ADMIN_INTERNAL_KEY', 'dev-admin-key-change-in-production')
        headers = {"X-Admin-Internal-Key": admin_key}
        response = requests.post(
            f"{API_BASE}/members/{member_id}/approve",
            headers=headers,
            timeout=REQUEST_TIMEOUT
        )
        response.raise_for_status()
        print(f"   ✅ 회원 승인 성공")
    except Exception as e:
        print(f"   ⚠️  회원 승인 실패: {e}")
        print("   계속 진행합니다...")
else:
    print(f"   ✅ 이미 APPROVED 상태임")

# Step 4: Request profile update magic link
print("\n4. 프로필 수정 인증 링크 요청...")
try:
    response = requests.post(
        f"{API_BASE}/auth/magic-link/profile-update",
        json={"email": "test@example.com"},
        timeout=REQUEST_TIMEOUT
    )
    response.raise_for_status()
    print("   ✅ 인증 링크 발송 성공")
except Exception as e:
    print(f"   ❌ 인증 링크 요청 실패: {e}")
    exit(1)

# Step 5: Get magic link from logs (for testing)
print("\n5. 매직링크 토큰 추출 (로그에서)...")
print("   💡 Docker 컨테이너 로그 확인 중...")

import subprocess
try:
    # Get logs from member-service
    result = subprocess.run(
        ["docker", "logs", "member-service", "--tail", "50"],
        capture_output=True,
        text=True
    )

    logs = result.stdout

    # Find the magic link URL
    import re
    pattern = r'token=([A-Za-z0-9._\-]+)'
    matches = re.findall(pattern, logs)

    if matches:
        # Get the last token
        token = matches[-1]
        print(f"   ✅ 토큰 추출 성공: {token[:20]}...")
    else:
        print("   ❌ 토큰을 찾을 수 없음")
        print("   💡 대신 직접 토큰 생성해서 테스트...")

        # Create a token directly
        from utils.token import create_magic_link_token
        token = create_magic_link_token("test@example.com", purpose="profile_update")
        print(f"   ✅ 직접 생성한 토큰: {token[:20]}...")

except Exception as e:
    print(f"   ❌ 로그 확인 실패: {e}")
    print("   💡 로컬에서 토큰 생성...")

    # Create token locally for testing
    import sys
    sys.path.insert(0, '.')
    from utils.token import create_magic_link_token
    token = create_magic_link_token("test@example.com", purpose="profile_update")
    print(f"   ✅ 생성된 토큰: {token[:20]}...")

# Step 6: Verify profile update token and get member data
print("\n6. 프로필 수정 토큰 검증 및 회원 정보 조회...")
try:
    response = requests.get(
        f"{API_BASE}/auth/verify-profile-update-json",
        params={"token": token},
        timeout=REQUEST_TIMEOUT
    )
    response.raise_for_status()
    member_data = response.json()
    print(f"   ✅ 토큰 검증 성공")
    print(f"      - 이름: {member_data['name']}")
    print(f"      - 자기소개: {member_data['description']}")
    print(f"      - 스킬: {[s['skill_name'] for s in member_data['skills']]}")
    links_str = [f"{link['link_type']}:{link['url']}" for link in member_data['links']]
    print(f"      - 링크: {links_str}")
except Exception as e:
    print(f"   ❌ 토큰 검증 실패: {e}")
    exit(1)

# Step 7: Update profile
print("\n7. 프로필 수정 요청...")
update_data = {
    "name": "수정된 이름",
    "description": "수정된 자기소개입니다",
    "image_url": "https://example.com/new-image.jpg",
    "skills": [
        {"skill_name": "Python"},
        {"skill_name": "TypeScript"},
        {"skill_name": "Docker"}
    ],
    "links": [
        {"link_type": "github", "url": "https://github.com/newuser"},
        {"link_type": "linkedin", "url": "https://linkedin.com/in/testuser"}
    ]
}

try:
    response = requests.put(
        f"{API_BASE}/members/{member_id}",
        params={"token": token},
        json=update_data,
        timeout=REQUEST_TIMEOUT
    )
    response.raise_for_status()
    updated_member = response.json()
    print(f"   ✅ 프로필 수정 성공")
    print(f"      - 이름: {member_data['name']} → {updated_member['name']}")
    print(f"      - 자기소개: {updated_member['description']}")
    print(f"      - 스킬: {[s['skill_name'] for s in updated_member['skills']]}")
    links_str = [f"{link['link_type']}:{link['url']}" for link in updated_member['links']]
    print(f"      - 링크: {links_str}")
except Exception as e:
    print(f"   ❌ 프로필 수정 실패: {e}")
    exit(1)

# Step 8: Verify the changes
print("\n8. 수정 사항 확인...")
try:
    response = requests.get(
        f"{API_BASE}/members/{member_id}",
        timeout=REQUEST_TIMEOUT
    )
    response.raise_for_status()
    final_member = response.json()

    assert final_member['name'] == "수정된 이름", "이름이 수정되지 않음"
    assert final_member['description'] == "수정된 자기소개입니다", "자기소개가 수정되지 않음"
    assert len(final_member['skills']) == 3, "스킬이 수정되지 않음"
    assert len(final_member['links']) == 2, "링크가 수정되지 않음"

    print("   ✅ 모든 수정 사항 확인 완료")
except Exception as e:
    print(f"   ❌ 확인 실패: {e}")
    exit(1)

print("\n" + "=" * 60)
print("✅ 모든 테스트 통과!")
print("=" * 60)
