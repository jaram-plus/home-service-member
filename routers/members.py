import logging

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, status, UploadFile
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
async def register_member(
    name: str = Form(...),
    email: str = Form(...),
    generation: int = Form(...),
    rank: str = Form(...),
    description: str | None = Form(None),
    image: UploadFile | None = File(None, description="프로필 이미지 (선택, JPG/PNG/WebP/GIF, 최대 5MB)"),
    skills: str = Form("[]", description="기술 스택 JSON 배열 (예: [{\"skill_name\":\"Python\"}])"),
    links: str = Form("[]", description="소셜 링크 JSON 배열 (예: [{\"link_type\":\"github\",\"url\":\"...\"}])"),
    service: MemberService = Depends(get_member_service),
):
    """
    Register a new member with optional profile image upload.

    Args:
        name: Member name
        email: Member email address
        generation: Generation number
        rank: Member rank (정회원, 준OB, OB)
        description: Self introduction (optional)
        image: Profile image file (optional)
        skills: JSON string of skills array
        links: JSON string of links array
        service: Member service

    Returns:
        Created member information

    Raises:
        HTTPException: If registration fails
    """
    try:
        member = await service.register_member_with_image(
            email=email,
            name=name,
            generation=generation,
            rank=rank,
            description=description,
            image_file=image,
            skills_json=skills,
            links_json=links,
        )
        return member
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e
    except RuntimeError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)) from e


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
async def update_member(
    member_id: int,
    name: str | None = Form(None),
    rank: str | None = Form(None),
    description: str | None = Form(None),
    image: UploadFile | None = File(None, description="새 프로필 이미지 (선택, 전송 시 기존 이미지 삭제됨)"),
    skills: str | None = Form(None, description="기술 스택 JSON 배열 (null인 경우 기존 값 유지)"),
    links: str | None = Form(None, description="소셜 링크 JSON 배열 (null인 경우 기존 값 유지)"),
    service: MemberService = Depends(get_member_service),
    _authenticated_member: Member = Depends(require_authenticated_member),
):
    """
    Update member profile (authenticated via Magic Link).

    본인만 수정 가능하며, Magic Link 토큰 인증이 필요합니다.

    Args:
        member_id: Member ID to update
        name: New name (optional)
        rank: New rank (optional)
        description: New description (optional)
        image: New profile image (optional)
        skills: JSON string of skills array (optional)
        links: JSON string of links array (optional)
        service: Member service
        _authenticated_member: Authenticated member from token

    Returns:
        Updated member

    Raises:
        HTTPException: 403 if trying to update another member's profile
        HTTPException: 400 if validation fails
    """
    try:
        # 본인 확인 (token_member_id == path_member_id)
        if _authenticated_member.id != member_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only update your own profile",
            )

        updated_member = await service.update_member_with_image(
            member_id=member_id,
            name=name,
            rank=rank,
            description=description,
            image_file=image,
            skills_json=skills,
            links_json=links,
        )
        return updated_member

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e
    except RuntimeError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)) from e


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
