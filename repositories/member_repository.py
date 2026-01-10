from typing import Self

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from models.link import Link
from models.member import Member, MemberStatus
from models.skill import Skill
from schemas.member import MemberCreate, MemberUpdate


class MemberRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    @classmethod
    def create(cls, db: Session) -> Self:
        return cls(db)

    def add_member(self, member_data: MemberCreate) -> Member:
        """Create a new member with skills and links"""
        db_member = Member(
            email=member_data.email,
            name=member_data.name,
            generation=member_data.generation,
            rank=member_data.rank,
            description=member_data.description,
            image_url=member_data.image_url,
            status=MemberStatus.UNVERIFIED,
        )

        self.db.add(db_member)
        self.db.flush()  # Get the ID before committing

        # Add skills
        for skill_data in member_data.skills:
            skill = Skill(member_id=db_member.id, skill_name=skill_data.skill_name)
            self.db.add(skill)

        # Add links
        for link_data in member_data.links:
            link = Link(member_id=db_member.id, link_type=link_data.link_type, url=link_data.url)
            self.db.add(link)

        self.db.commit()
        self.db.refresh(db_member)
        return db_member

    def get_member_by_id(self, member_id: int) -> Member | None:
        """Get member by ID"""
        return self.db.query(Member).filter(Member.id == member_id).first()

    def get_member_by_email(self, email: str) -> Member | None:
        """Get member by email"""
        return self.db.query(Member).filter(Member.email == email).first()

    def get_all_members(self, status: MemberStatus | None = None) -> list[Member]:
        """Get all members, optionally filtered by status"""
        query = self.db.query(Member)
        if status:
            query = query.filter(Member.status == status)
        return query.all()

    def update_member(self, member: Member, update_data: MemberUpdate) -> Member:
        """Update member data"""
        if update_data.name is not None:
            member.name = update_data.name
        # rank, email, generation cannot be updated
        if update_data.description is not None:
            member.description = update_data.description
        if update_data.image_url is not None:
            member.image_url = update_data.image_url

        # Update skills if provided
        if update_data.skills is not None:
            # Delete existing skills
            self.db.query(Skill).filter(Skill.member_id == member.id).delete()
            # Add new skills
            for skill_data in update_data.skills:
                skill = Skill(member_id=member.id, skill_name=skill_data.skill_name)
                self.db.add(skill)

        # Update links if provided
        if update_data.links is not None:
            # Delete existing links
            self.db.query(Link).filter(Link.member_id == member.id).delete()
            # Add new links
            for link_data in update_data.links:
                link = Link(member_id=member.id, link_type=link_data.link_type, url=link_data.url)
                self.db.add(link)

        self.db.commit()
        self.db.refresh(member)
        return member

    def update_member_status(self, member: Member, status: MemberStatus) -> Member:
        """Update member status (for admin approval/rejection)"""
        member.status = status
        self.db.commit()
        self.db.refresh(member)
        return member

    def delete_member(self, member: Member) -> None:
        """Delete a member"""
        self.db.delete(member)
        self.db.commit()
