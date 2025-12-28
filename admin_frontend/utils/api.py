"""API client for Admin Frontend.

Matches FastAPI endpoints:
- GET /members?status=xxx -> list[MemberResponse] (X-Admin-Key header required)
- GET /members/{member_id} -> MemberResponse (X-Admin-Key header required)
- POST /members/{member_id}/approve -> MemberResponse (X-Admin-Key header required)
- POST /members/{member_id}/reject -> 204 No Content (X-Admin-Key header required)
- DELETE /members/{member_id} -> 204 No Content (X-Admin-Key header required)
"""

import os

import requests

ADMIN_KEY = os.getenv("ADMIN_API_KEY")
API_BASE = os.getenv("API_BASE_URL", "http://localhost:8000")


# Enums matching Backend
class MemberStatus:
    UNVERIFIED = "UNVERIFIED"
    PENDING = "PENDING"
    APPROVED = "APPROVED"


class MemberRank:
    REGULAR = "정회원"
    OB = "OB"
    PROSPECTIVE_OB = "준OB"


def _headers() -> dict[str, str]:
    """Get headers with admin API key."""
    if not ADMIN_KEY:
        raise ValueError("ADMIN_API_KEY environment variable is not set")
    return {"X-Admin-Key": ADMIN_KEY}


def get_all_members(status: str | None = None) -> list[dict]:
    """
    Get all members, optionally filtered by status.

    GET /members?status=xxx

    Query params:
        status: MemberStatus (UNVERIFIED, PENDING, APPROVED) | None

    Response: list[MemberResponse]

    Headers: X-Admin-Key
    """
    params = {}
    if status:
        params["status"] = status

    response = requests.get(
        f"{API_BASE}/members",
        headers=_headers(),
        params=params,
        timeout=10,
    )
    response.raise_for_status()
    return response.json()


def get_member(member_id: int) -> dict:
    """
    Get member by ID.

    GET /members/{member_id}

    Response: MemberResponse

    Headers: X-Admin-Key
    """
    response = requests.get(
        f"{API_BASE}/members/{member_id}",
        headers=_headers(),
        timeout=10,
    )
    response.raise_for_status()
    return response.json()


def approve_member(member_id: int) -> dict:
    """
    Approve a member registration.

    POST /members/{member_id}/approve

    Response: MemberResponse

    Headers: X-Admin-Key
    """
    response = requests.post(
        f"{API_BASE}/members/{member_id}/approve",
        headers=_headers(),
        timeout=10,
    )
    response.raise_for_status()
    return response.json()


def reject_member(member_id: int) -> None:
    """
    Reject a member registration (deletes from DB).

    POST /members/{member_id}/reject

    Response: 204 No Content

    Headers: X-Admin-Key
    """
    response = requests.post(
        f"{API_BASE}/members/{member_id}/reject",
        headers=_headers(),
        timeout=10,
    )
    response.raise_for_status()


def delete_member(member_id: int) -> None:
    """
    Delete a member.

    DELETE /members/{member_id}

    Response: 204 No Content

    Headers: X-Admin-Key
    """
    response = requests.delete(
        f"{API_BASE}/members/{member_id}",
        headers=_headers(),
        timeout=10,
    )
    response.raise_for_status()
