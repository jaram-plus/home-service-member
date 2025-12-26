#!/usr/bin/env python
"""
Full flow test: 회원가입 → 이메일인증 → 관리자승인
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from database import SessionLocal
from models.member import Member, MemberStatus
from repositories.member_repository import MemberRepository
from schemas.member import MemberCreate

def test_full_flow():
    db = SessionLocal()
    repo = MemberRepository.create(db)

    print("=== 1. Create member with UNVERIFIED status ===")
    member_data = MemberCreate(
        email="fullflow@example.com",
        name="플로우테스트",
        generation=41,
        rank="정회원",
        description="전체 플로우 테스트",
        skills=[{"skill_name": "Docker"}],
        links=[{"link_type": "github", "url": "https://github.com/fullflow"}]
    )

    member = repo.add_member(member_data)
    print(f"✅ Member created: {member.name}")
    print(f"   Status: {member.status}")
    print(f"   Expected: UNVERIFIED")
    assert member.status == MemberStatus.UNVERIFIED, "Status should be UNVERIFIED"

    print("\n=== 2. Simulate email verification (UNVERIFIED → PENDING) ===")
    member = repo.update_member_status(member, MemberStatus.PENDING)
    print(f"✅ Status updated: {member.status}")
    print(f"   Expected: PENDING")
    assert member.status == MemberStatus.PENDING, "Status should be PENDING"

    print("\n=== 3. Admin approval (PENDING → APPROVED) ===")
    member = repo.update_member_status(member, MemberStatus.APPROVED)
    print(f"✅ Status updated: {member.status}")
    print(f"   Expected: APPROVED")
    assert member.status == MemberStatus.APPROVED, "Status should be APPROVED"

    print("\n=== 4. Test rejection (delete from DB) ===")
    member_id = member.id
    repo.delete_member(member)

    deleted_member = repo.get_member_by_id(member_id)
    print(f"✅ Member deleted: {deleted_member is None}")
    print(f"   Expected: True")
    assert deleted_member is None, "Member should be deleted"

    print("\n🎉 All tests passed!")
    db.close()
    return True

if __name__ == "__main__":
    try:
        test_full_flow()
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
