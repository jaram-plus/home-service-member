import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db
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
    service: MemberService = Depends(get_member_service),
):
    """Update member profile (requires authentication via magic link)"""
    try:
        updated_member = service.update_member(member_id, update_data)
        return updated_member
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/{member_id}/approve", response_model=MemberResponse)
def approve_member(member_id: int, service: MemberService = Depends(get_member_service)):
    """Approve a member registration (admin only)"""
    try:
        member = service.approve_member(member_id)
        return member
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/{member_id}/reject", status_code=status.HTTP_204_NO_CONTENT)
def reject_member(member_id: int, service: MemberService = Depends(get_member_service)):
    """Reject a member registration (admin only) - Deletes member from DB"""
    try:
        service.reject_member(member_id)
        return None
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.delete("/{member_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_member(member_id: int, service: MemberService = Depends(get_member_service)):
    """Delete a member (admin only)"""
    try:
        service.delete_member(member_id)
        return None
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
