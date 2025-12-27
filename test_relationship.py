#!/usr/bin/env python
"""
Test script to verify skills and links are loaded correctly
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from database import SessionLocal
from models.member import Member
from models.skill import Skill
from models.link import Link
from schemas.member import MemberCreate
from services.member_service import MemberService

# Create test data
def test_relationship():
    db = SessionLocal()
    service = MemberService(db)

    try:
        # Create a test member
        member_data = MemberCreate(
            email="relationship_test@example.com",
            name="관계테스트",
            generation=41,
            rank="정회원",
            description="관계 테스트용 멤버",
            skills=[
                {"skill_name": "Python"},
                {"skill_name": "FastAPI"}
            ],
            links=[
                {"link_type": "github", "url": "https://github.com/test"},
                {"link_type": "blog", "url": "https://blog.test.com"}
            ],
            image_url="https://example.com/image.jpg"
        )

        print("=== Creating member ===")
        member = service.register_member(member_data)
        print(f"✅ Member created: {member.name} (ID: {member.id})")
        print(f"   Status: {member.status}")

        # Fetch member from DB to test relationships
        print("\n=== Fetching member from DB ===")
        db_member = db.query(Member).filter(Member.id == member.id).first()

        if db_member:
            print(f"✅ Member found: {db_member.name}")
            print(f"   Email: {db_member.email}")
            print(f"   Skills count: {len(db_member.skills)}")
            print(f"   Links count: {len(db_member.links)}")

            print("\n   Skills:")
            for skill in db_member.skills:
                print(f"     - {skill.skill_name}")

            print("\n   Links:")
            for link in db_member.links:
                print(f"     - {link.link_type}: {link.url}")

            # Check if relationships are working
            if len(db_member.skills) == 2 and len(db_member.links) == 2:
                print("\n✅ SUCCESS: Relationships are working correctly!")
                print(f"   Skills: {[s.skill_name for s in db_member.skills]}")
                print(f"   Links: {[l.link_type for l in db_member.links]}")
            else:
                print("\n❌ FAILED: Relationships not loaded properly")
                print(f"   Expected 2 skills, got {len(db_member.skills)}")
                print(f"   Expected 2 links, got {len(db_member.links)}")
                return False
        else:
            print("❌ Member not found in database")
            return False

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()

    return True


if __name__ == "__main__":
    success = test_relationship()
    sys.exit(0 if success else 1)
