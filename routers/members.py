import json
import logging

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile, status
from sqlalchemy.orm import Session

from database import get_db
from dependencies import require_internal_admin
from models.member import Member, MemberStatus
from schemas.member import MemberCreate, MemberResponse, MemberUpdate
from services.member_service import MemberService
from services.storage_service import StorageService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/members", tags=["members"])


def get_member_service(db: Session = Depends(get_db)) -> MemberService:
    """Dependency to get member service"""
    return MemberService(db)


def get_storage_service() -> StorageService:
    """Dependency to get storage service"""
    return StorageService()


@router.post("/register", response_model=MemberResponse, status_code=status.HTTP_201_CREATED)
async def register_member(
    name: str = Form(...),
    email: str = Form(...),
    generation: int = Form(...),
    rank: str = Form(...),
    description: str | None = Form(None),
    image: UploadFile | None = File(None),
    skills: str | None = Form(None),  # JSON string
    links: str | None = Form(None),  # JSON string
    service: MemberService = Depends(get_member_service),
    storage: StorageService = Depends(get_storage_service),
):
    """
    Register a new member with multipart/form-data support for image upload.

    Args:
        name: Member name
        email: Member email
        generation: Member generation number
        rank: Member rank (정회원, OB, 준OB)
        description: Optional description
        image: Optional profile image file
        skills: JSON string of skills array
        links: JSON string of links array
    """
    try:
        # Handle image upload
        image_url = None
        if image and image.filename:
            file_content = await image.read()
            image_url = storage.upload_image(
                file_data=file_content,
                filename=image.filename,
                content_type=image.content_type or "image/jpeg",
            )

        # Parse skills and links from JSON strings
        skills_list = json.loads(skills) if skills else []
        links_list = json.loads(links) if links else []

        # Create member data
        member_data = MemberCreate(
            email=email,
            name=name,
            generation=generation,
            rank=rank,
            description=description,
            image_url=image_url,
            skills=skills_list,
            links=links_list,
        )

        member = service.register_member(member_data)
        return member

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid JSON format: {e}")


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
    token: str = Form(...),
    name: str | None = Form(None),
    description: str | None = Form(None),
    image: UploadFile | None = File(None),
    skills: str | None = Form(None),  # JSON string
    links: str | None = Form(None),  # JSON string
    service: MemberService = Depends(get_member_service),
    storage: StorageService = Depends(get_storage_service),
):
    """
    Update member profile with multipart/form-data support for image upload.
    Requires valid magic link token.

    Args:
        member_id: Member ID to update
        token: Magic link token for authentication
        name: New name (optional)
        description: New description (optional)
        image: New profile image file (optional)
        skills: JSON string of skills array (optional)
        links: JSON string of links array (optional)
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

        # Handle image upload
        image_url = None
        if image and image.filename:
            # Delete old image if exists
            if member.image_url:
                storage.delete_image(member.image_url)

            # Upload new image
            file_content = await image.read()
            image_url = storage.upload_image(
                file_data=file_content,
                filename=image.filename,
                content_type=image.content_type or "image/jpeg",
            )

        # Parse skills and links from JSON strings
        skills_list = json.loads(skills) if skills else None
        links_list = json.loads(links) if links else None

        # Create update data
        update_data = MemberUpdate(
            name=name,
            description=description,
            image_url=image_url,
            skills=skills_list,
            links=links_list,
        )

        # Filter out None values
        update_data_dict = update_data.model_dump(exclude_none=True)

        # 수정 처리
        updated_member = service.update_member(member_id, MemberUpdate(**update_data_dict))
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
