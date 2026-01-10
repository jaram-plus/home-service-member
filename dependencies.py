"""FastAPI dependencies for authentication and authorization."""

import secrets

from fastapi import Header, HTTPException, Query, status, Depends
from sqlalchemy.orm import Session

from config import settings
from database import get_db
from models.member import Member
from services.member_service import MemberService
from utils.token import verify_magic_link_token


async def require_internal_admin(x_admin_key: str = Header(...)) -> bool:
    """
    Require internal admin API key for admin-only endpoints.

    This dependency validates that requests from admin frontends include
    the correct admin API key in the X-Admin-Key header.

    The admin frontend should read ADMIN_API_KEY from environment and
    include it in every request to protected endpoints.

    Args:
        x_admin_key: The admin API key from X-Admin-Key header

    Returns:
        True if authentication succeeds

    Raises:
        HTTPException: 403 if the key is invalid
    """
    if not secrets.compare_digest(str(x_admin_key), str(settings.admin_internal_key)):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid admin API key"
        )
    return True


async def require_authenticated_member(
    token: str = Query(..., description="Magic Link token for authentication"),
    db: Session = Depends(get_db),
) -> Member:
    """
    Require authenticated member via Magic Link token.

    This dependency validates Magic Link tokens and returns the authenticated
    member. Used for profile update endpoints.

    Args:
        token: Magic Link token (purpose="profile_update")
        db: Database session

    Returns:
        Authenticated Member object

    Raises:
        HTTPException: 401 if token is invalid/expired
        HTTPException: 404 if member not found
    """
    # purpose="profile_update"로 토큰 검증
    email = verify_magic_link_token(token, purpose="profile_update")
    if not email:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired authentication token",
        )

    service = MemberService(db)
    member = service.get_member_by_email(email)
    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Member not found",
        )

    return member