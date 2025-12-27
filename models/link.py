from __future__ import annotations

from enum import Enum

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base


class LinkType(str, Enum):
    GITHUB = "github"
    LINKEDIN = "linkedin"
    BLOG = "blog"
    INSTAGRAM = "instagram"
    NOTION = "notion"
    SOLVED_AC = "solved_ac"


class Link(Base):
    __tablename__ = "member_link"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    member_id: Mapped[int] = mapped_column(ForeignKey("member.id", ondelete="CASCADE"), nullable=False)
    link_type: Mapped[LinkType] = mapped_column(nullable=False)
    url: Mapped[str] = mapped_column(String(500), nullable=False)

    # Relationship
    member: Mapped["Member"] = relationship(back_populates="links")
