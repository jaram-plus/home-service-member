from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum

from sqlalchemy import DateTime, Enum as SQLEnum, func, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base


class MemberStatus(str, Enum):
    UNVERIFIED = "unverified"  # 이메일 인증 전
    PENDING = "pending"  # 이메일 인증 완료, 관리자 승인 대기
    APPROVED = "approved"  # 관리자 승인 완료


class MemberRank(str, Enum):
    REGULAR = "정회원"
    OB = "OB"
    PROSPECTIVE_OB = "준OB"


class Member(Base):
    __tablename__ = "member"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    generation: Mapped[int] = mapped_column(nullable=False)  # 기수
    rank: Mapped[MemberRank] = mapped_column(SQLEnum(MemberRank), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    image_url: Mapped[str | None] = mapped_column(String(500), nullable=True)

    status: Mapped[MemberStatus] = mapped_column(
        SQLEnum(MemberStatus),
        default=MemberStatus.UNVERIFIED,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        server_onupdate=func.now(),
        nullable=False,
    )

    # Relationships
    skills: Mapped[list["Skill"]] = relationship(
        back_populates="member", cascade="all, delete-orphan", lazy="selectin"
    )
    links: Mapped[list["Link"]] = relationship(
        back_populates="member", cascade="all, delete-orphan", lazy="selectin"
    )
