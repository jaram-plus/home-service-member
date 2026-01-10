"""API client for User Frontend.

Matches FastAPI endpoints:
- POST /members/register -> multipart/form-data -> MemberResponse
- POST /auth/magic-link/profile-update -> {email} -> {message}
- GET /auth/verify?token=xxx -> MagicLinkVerifyResponse
- PUT /members/{member_id} -> multipart/form-data -> MemberResponse
"""

import json
import os

import requests

API_BASE = os.getenv("API_BASE_URL", "http://localhost:8000")


# Enums matching Backend
class MemberRank:
    REGULAR = "정회원"
    OB = "OB"
    PROSPECTIVE_OB = "준OB"


def register_member(
    name: str,
    email: str,
    generation: int,
    rank: str,
    description: str = "",
    image_url: str | None = None,
    skills: list[dict] | None = None,
    links: list[dict] | None = None,
) -> dict:
    """
    Register a new member.

    POST /members/register

    Request body (MemberCreate):
        email: EmailStr
        name: str
        generation: int
        rank: MemberRank (정회원, OB, 준OB)
        description: str | None
        image_url: str | None
        skills: list[SkillCreate] = []
        links: list[LinkCreate] = []

    Response: MemberResponse
    """
    response = requests.post(
        f"{API_BASE}/members/register",
        json={
            "email": email,
            "name": name,
            "generation": generation,
            "rank": rank,
            "description": description or None,
            "image_url": image_url,
            "skills": skills or [],
            "links": links or [],
        },
        timeout=10,
    )
    response.raise_for_status()
    return response.json()


def register_member_with_image(
    name: str,
    email: str,
    generation: int,
    rank: str,
    description: str = "",
    image_file=None,
    skills: list[dict] | None = None,
    links: list[dict] | None = None,
) -> dict:
    """
    Register a new member with optional profile image upload (multipart/form-data).

    POST /members/register

    Request body (multipart/form-data):
        name: str
        email: str
        generation: int
        rank: str
        description: str | None
        image: UploadFile | None
        skills: str (JSON string)
        links: str (JSON string)

    Response: MemberResponse
    """
    files = None
    if image_file:
        # Streamlit UploadedFile / file-like 모두 방어적으로 처리
        filename = getattr(image_file, "name", "profile")
        content_type = getattr(image_file, "type", None)
        try:
            image_file.seek(0)
        except Exception:
            pass
        if content_type:
            files = {"image": (filename, image_file, content_type)}
        else:
            files = {"image": (filename, image_file)}

    data = {
        "name": name,
        "email": email,
        "generation": str(generation),
        "rank": rank,
        "description": description or "",
        "skills": json.dumps(skills or [], ensure_ascii=False),
        "links": json.dumps(links or [], ensure_ascii=False),
    }

    response = requests.post(
        f"{API_BASE}/members/register",
        files=files,
        data=data,
        timeout=30,
    )
    response.raise_for_status()
    return response.json()


def request_profile_update_link(email: str) -> None:
    """
    Request a magic link for profile update.

    POST /auth/magic-link/profile-update

    Request body:
        email: str

    Response: {message: str}
    """
    response = requests.post(
        f"{API_BASE}/auth/magic-link/profile-update",
        json={"email": email},
        timeout=10,
    )
    response.raise_for_status()


def verify_token(token: str) -> dict:
    """
    Verify a magic link token.

    GET /auth/verify?token=xxx

    Response:
        email: str
        message: str
    """
    response = requests.get(
        f"{API_BASE}/auth/verify",
        params={"token": token, "purpose": "profile_update"},
        timeout=10,
    )
    response.raise_for_status()
    return response.json()


def update_member_with_image(
    member_id: int,
    token: str,
    name: str | None = None,
    rank: str | None = None,
    description: str | None = None,
    image_file=None,
    skills: list[dict] | None = None,
    links: list[dict] | None = None,
) -> dict:
    """
    Update member profile with authentication token (multipart/form-data).

    PUT /members/{member_id}?token=xxx

    Request body (multipart/form-data):
        name: str | None
        rank: str | None
        description: str | None
        image: UploadFile | None
        skills: str | None (JSON string)
        links: str | None (JSON string)

    Response: MemberResponse
    """
    files = None
    if image_file:
        # Streamlit UploadedFile / file-like 모두 방어적으로 처리
        filename = getattr(image_file, "name", "profile")
        content_type = getattr(image_file, "type", None)
        try:
            image_file.seek(0)
        except Exception:
            pass
        if content_type:
            files = {"image": (filename, image_file, content_type)}
        else:
            files = {"image": (filename, image_file)}

    data = {}
    if name is not None:
        data["name"] = name
    if rank is not None:
        data["rank"] = rank
    if description is not None:
        data["description"] = description
    if skills is not None:
        data["skills"] = json.dumps(skills, ensure_ascii=False)
    if links is not None:
        data["links"] = json.dumps(links, ensure_ascii=False)

    response = requests.put(
        f"{API_BASE}/members/{member_id}",
        params={"token": token},
        files=files,
        data=data,
        timeout=30,
    )
    response.raise_for_status()
    return response.json()

