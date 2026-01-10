from datetime import datetime

from pydantic import BaseModel, EmailStr

from models.member import MemberRank, MemberStatus
from models.link import LinkType


# Skill schemas
class SkillCreate(BaseModel):
    skill_name: str


class SkillResponse(BaseModel):
    id: int
    skill_name: str

    model_config = {"from_attributes": True}


# Link schemas
class LinkCreate(BaseModel):
    link_type: LinkType
    url: str


class LinkResponse(BaseModel):
    id: int
    link_type: LinkType
    url: str

    model_config = {"from_attributes": True}


# Member schemas
class MemberBase(BaseModel):
    email: EmailStr
    name: str
    generation: int
    rank: MemberRank
    description: str | None = None


class MemberCreate(MemberBase):
    skills: list[SkillCreate] = []
    links: list[LinkCreate] = []
    # image_url 제거 - 파일 업로드로 대체


class MemberUpdate(BaseModel):
    name: str | None = None
    rank: MemberRank | None = None
    description: str | None = None
    skills: list[SkillCreate] | None = None
    links: list[LinkCreate] | None = None
    image_url: str | None = None


class MemberResponse(MemberBase):
    id: int
    status: MemberStatus
    image_url: str | None
    created_at: datetime
    updated_at: datetime
    skills: list[SkillResponse] = []
    links: list[LinkResponse] = []

    model_config = {"from_attributes": True}


class MagicLinkRequest(BaseModel):
    email: EmailStr


class MagicLinkVerify(BaseModel):
    token: str
