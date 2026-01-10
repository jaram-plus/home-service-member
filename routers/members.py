import logging

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from database import get_db
from dependencies import require_internal_admin
from models.member import Member, MemberStatus
from schemas.member import MemberCreate, MemberResponse, MemberUpdate
from services.member_service import MemberService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/members", tags=["members"])


def get_member_service(db: Session = Depends(get_db)) -> MemberService:
    """Dependency to get member service"""
    return MemberService(db)


@router.post("/register", response_model=MemberResponse, status_code=status.HTTP_201_CREATED)
def register_member(member_data: MemberCreate, service: MemberService = Depends(get_member_service)):
    """Register a new member"""
    try:
        member = service.register_member(member_data)
        return member
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/{member_id}", response_model=MemberResponse)
def get_member(member_id: int, service: MemberService = Depends(get_member_service)):
    """Get member by ID"""
    member = service.get_member_by_id(member_id)
    if not member:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Member not found")
    return member


@router.get("", response_model=list[MemberResponse])
def get_all_members(
    status: MemberStatus | None = None, service: MemberService = Depends(get_member_service)
):
    """Get all members, optionally filtered by status"""
    members = service.get_all_members(status)
    return members


@router.put("/{member_id}", response_model=MemberResponse)
def update_member(
    member_id: int,
    update_data: MemberUpdate,
    token: str = Query(..., description="Magic link token for profile update"),
    service: MemberService = Depends(get_member_service),
):
    """
    Update member profile (requires valid magic link token)

    The token must be a valid profile_update token and must match the member's email.
    Only approved members can update their profiles.
    """
    try:
        # 토큰 검증 및 본인 확인
        member = service.verify_profile_update_token(token)

        # 본인 확인: 토큰의 회원 ID와 수정하려는 회원의 ID 일치 확인
        if member.id != member_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Unauthorized: Token does not match this member. You can only update your own profile."
            )

        # 수정 처리
        updated_member = service.update_member(member_id, update_data)
        return updated_member

    except ValueError as e:
        error_msg = str(e)
        # 적절한 상태 코드 반환
        if "not found" in error_msg.lower():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=error_msg) from e
        if "Only approved members" in error_msg or "does not match" in error_msg:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=error_msg) from e
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=error_msg) from e
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error updating member {member_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred"
        ) from e


@router.post("/{member_id}/approve", response_model=MemberResponse)
def approve_member(
    member_id: int,
    service: MemberService = Depends(get_member_service),
    _admin: bool = Depends(require_internal_admin),
):
    """Approve a member registration (admin only)"""
    try:
        member = service.approve_member(member_id)
        return member
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/{member_id}/reject", status_code=status.HTTP_204_NO_CONTENT)
def reject_member(
    member_id: int,
    service: MemberService = Depends(get_member_service),
    _admin: bool = Depends(require_internal_admin),
):
    """Reject a member registration (admin only) - Deletes member from DB"""
    try:
        service.reject_member(member_id)
        return None
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.delete("/{member_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_member(
    member_id: int,
    service: MemberService = Depends(get_member_service),
    _admin: bool = Depends(require_internal_admin),
):
    """Delete a member (admin only)"""
    try:
        service.delete_member(member_id)
        return None
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
