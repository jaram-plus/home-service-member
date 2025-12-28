"""API client for User Frontend.

Matches FastAPI endpoints:
- POST /members/register -> MemberCreate -> MemberResponse
- POST /auth/magic-link/profile-update -> {email} -> {message}
- GET /auth/verify?token=xxx -> MagicLinkVerifyResponse
"""

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
        params={"token": token},
        timeout=10,
    )
    response.raise_for_status()
    return response.json()

