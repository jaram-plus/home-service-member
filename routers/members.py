import logging

from fastapi import APIRouter, Depends, HTTPException, status
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


@router.put("/{member_id}", response_model=MemberResponse, include_in_schema=False)
def update_member(
    member_id: int,
    update_data: MemberUpdate,
    service: MemberService = Depends(get_member_service),
):
    """
    Update member profile (DISABLED - TODO: Implement authentication)

    TODO: Magic Link 인증 후에만 수정 가능하도록 구현 필요
    - 토큰에서 이메일 추출
    - 본인 확인 (member.email == token.email)
    - 또는 세션 기반 인증

    Ref: 251220-project-specification-meeting-note.md (Profile Update Sequence)
    """
    # TODO: Implement authentication check
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Profile update is currently disabled. Authentication via Magic Link required."
    )


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
