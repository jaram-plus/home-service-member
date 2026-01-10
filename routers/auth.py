import logging

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database import get_db
from schemas.member import MagicLinkRequest
from services.member_service import MemberService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["auth"])


class MagicLinkVerifyResponse(BaseModel):
    """Response model for magic link verification"""

    email: str
    message: str


def get_member_service(db: Session = Depends(get_db)) -> MemberService:
    """Dependency to get member service"""
    return MemberService(db)


@router.post("/magic-link/profile-update")
def request_profile_update_link(
    request: MagicLinkRequest, service: MemberService = Depends(get_member_service)
):
    """Request magic link for profile update"""
    try:
        service.request_profile_update(request.email)
        return {"message": "Magic link sent to your email"}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e


@router.get("/verify", response_model=MagicLinkVerifyResponse)
def verify_magic_link(
    token: str = Query(..., description="Magic link token"),
    purpose: str = Query("registration", description="Token purpose: 'registration' or 'profile_update'"),
    service: MemberService = Depends(get_member_service),
):
    """
    Verify magic link token.

    Supports two purposes:
    - 'registration': Initial email verification (UNVERIFIED -> PENDING)
    - 'profile_update': Profile update authentication (returns email)
    """
    try:
        if purpose == "registration":
            member = service.verify_email(token)
            return MagicLinkVerifyResponse(
                email=member.email, message="Email verified successfully. Status changed to PENDING."
            )
        elif purpose == "profile_update":
            email = service.verify_magic_link(token, purpose="profile_update")
            return MagicLinkVerifyResponse(
                email=email, message="Authentication successful. You can now update your profile."
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid purpose: {purpose}. Allowed: 'registration', 'profile_update'",
            )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e)) from e
