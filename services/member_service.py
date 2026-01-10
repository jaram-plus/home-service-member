import json
import logging
import os
import tempfile
from urllib.parse import quote

from config import settings
from fastapi import UploadFile
from models.link import Link
from models.member import Member, MemberStatus
from models.skill import Skill
from repositories.member_repository import MemberRepository
from schemas.member import MemberCreate, MemberUpdate
from services.email_service import EmailService
from services.email_service_impl import create_email_service
from services.file_validation_service import FileValidationService
from services.storage_service_impl import create_storage_service
from sqlalchemy.orm import Session
from utils.token import create_magic_link_token, verify_magic_link_token

logger = logging.getLogger(__name__)


class MemberService:
    def __init__(self, db: Session, email_service: EmailService | None = None):
        self.db = db
        self.email_service = email_service or create_email_service()
        self.storage_service = create_storage_service()

    @staticmethod
    def _build_magic_link_url(token: str) -> str:
        """Build magic link URL using configurable base URL."""
        base_url = settings.base_url.rstrip("/")
        encoded_token = quote(token, safe="")
        return f"{base_url}/auth/verify?token={encoded_token}"

    def register_member(self, member_data: MemberCreate) -> Member:
        """Register a new member"""
        member_repo = MemberRepository.create(self.db)

        # Check if email already exists
        existing_member = member_repo.get_member_by_email(member_data.email)
        if existing_member:
            raise ValueError(f"Member with email {member_data.email} already exists")

        # Create member with UNVERIFIED status
        member = member_repo.add_member(member_data)
        logger.info(f"Member registered: {member.email}, status: UNVERIFIED")

        # Send magic link for verification
        token = create_magic_link_token(member_data.email, purpose="registration")
        magic_link_url = self._build_magic_link_url(token)
        self.email_service.send_magic_link(member_data.email, magic_link_url)

        return member

    async def register_member_with_image(
        self,
        email: str,
        name: str,
        generation: int,
        rank: str,
        description: str | None,
        image_file: UploadFile | None,
        skills_json: str,
        links_json: str,
    ) -> Member:
        """
        Register a new member with optional profile image upload.

        Args:
            email: Member email
            name: Member name
            generation: Generation number
            rank: Member rank
            description: Self introduction
            image_file: Profile image file (optional)
            skills_json: JSON string of skills array
            links_json: JSON string of links array

        Returns:
            Created member

        Raises:
            ValueError: If validation fails or member already exists
            RuntimeError: If storage operation fails
        """
        member_repo = MemberRepository.create(self.db)
        temp_file_path = None

        try:
            # 1. 스킬/링크 JSON 파싱 (안전하게, 에러 처리 포함)
            try:
                skills_data = json.loads(skills_json) if skills_json else []
                links_data = json.loads(links_json) if links_json else []
            except json.JSONDecodeError as e:
                raise ValueError(f"Invalid JSON format for skills/links: {e}") from e

            # 2. 이미지 검증 (이미지가 있는 경우에만)
            if image_file:
                await FileValidationService.validate_profile_image(image_file)

                # 임시 파일 저장
                with tempfile.NamedTemporaryFile(delete=False, suffix=".tmp") as tmp:
                    content = await image_file.read()
                    tmp.write(content)
                    temp_file_path = tmp.name

            # 3. 회원 생성 (DB flush로 member_id 획득)
            existing_member = member_repo.get_member_by_email(email)
            if existing_member:
                raise ValueError(f"Member with email {email} already exists")

            member = Member(
                email=email,
                name=name,
                generation=generation,
                rank=rank,
                description=description,
                status=MemberStatus.UNVERIFIED,
            )
            self.db.add(member)
            self.db.flush()  # member.id 생성

            # 4. 이미지 S3 업로드 (이미지가 있는 경우에만)
            if temp_file_path:
                try:
                    image_url = await self.storage_service.upload_profile_image(
                        temp_file_path,
                        member.id,
                        image_file.filename or "profile.jpg",
                    )
                    member.image_url = image_url
                    logger.info(f"Profile image uploaded for member {member.id}: {image_url}")
                except Exception as e:
                    logger.error(f"Failed to upload profile image: {e}")
                    # 이미지 업로드 실패 시에도 회원가입은 계속 진행
                    # 이미지는 나중에 업데이트 가능

            # 5. 스킬 추가
            for skill_data in skills_data:
                if isinstance(skill_data, dict) and "skill_name" in skill_data:
                    skill = Skill(member_id=member.id, skill_name=skill_data["skill_name"])
                    self.db.add(skill)

            # 6. 링크 추가
            for link_data in links_data:
                if isinstance(link_data, dict) and "link_type" in link_data and "url" in link_data:
                    link = Link(
                        member_id=member.id,
                        link_type=link_data["link_type"],
                        url=link_data["url"],
                    )
                    self.db.add(link)

            # 7. 커밋
            self.db.commit()
            self.db.refresh(member)

            # 8. Magic Link 발송
            token = create_magic_link_token(email, purpose="registration")
            magic_link_url = self._build_magic_link_url(token)
            self.email_service.send_magic_link(email, magic_link_url)

            logger.info(f"Member registered: {email}, status: UNVERIFIED")
            return member

        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to register member: {e}")

            # 실패 시 업로드된 파일 삭제
            if temp_file_path and os.path.exists(temp_file_path):
                try:
                    os.unlink(temp_file_path)
                    logger.info(f"Cleaned up temporary file: {temp_file_path}")
                except Exception as cleanup_error:
                    logger.error(f"Failed to clean up temporary file: {cleanup_error}")

            raise e

        finally:
            # 임시 파일 정리
            if temp_file_path and os.path.exists(temp_file_path):
                try:
                    os.unlink(temp_file_path)
                except Exception:
                    pass

    def request_profile_update(self, email: str) -> str:
        """Request to update profile by sending magic link"""
        member_repo = MemberRepository.create(self.db)
        member = member_repo.get_member_by_email(email)

        if not member:
            raise ValueError(f"Member with email {email} not found")

        # Send magic link for profile update
        token = create_magic_link_token(email, purpose="profile_update")
        magic_link_url = self._build_magic_link_url(token)
        self.email_service.send_magic_link(email, magic_link_url)

        logger.info(f"Profile update requested for: {email}")
        return magic_link_url

    def verify_magic_link(self, token: str, purpose: str = "auth") -> str:
        """Verify magic link token and return email"""
        email = verify_magic_link_token(token, purpose)
        if not email:
            raise ValueError("Invalid or expired token")
        return email

    def get_member_from_token(self, token: str, purpose: str = "profile_update") -> Member:
        """
        Get member from Magic Link token.

        Args:
            token: Magic Link token
            purpose: Token purpose (default: "profile_update")

        Returns:
            Member object

        Raises:
            ValueError: If token is invalid or member not found
        """
        email = verify_magic_link_token(token, purpose)
        if not email:
            raise ValueError("Invalid or expired token")

        member = self.get_member_by_email(email)
        if not member:
            raise ValueError(f"Member not found: {email}")

        return member

    def verify_email(self, token: str) -> Member:
        """Verify email and change status from UNVERIFIED to PENDING"""
        email = verify_magic_link_token(token, purpose="registration")
        if not email:
            raise ValueError("Invalid or expired token")

        member_repo = MemberRepository.create(self.db)
        member = member_repo.get_member_by_email(email)

        if not member:
            raise ValueError(f"Member with email {email} not found")

        if member.status != MemberStatus.UNVERIFIED:
            raise ValueError(f"Member status is not UNVERIFIED (current: {member.status})")

        # Change status to PENDING
        member = member_repo.update_member_status(member, MemberStatus.PENDING)
        logger.info(f"Email verified, status changed to PENDING: {email}")

        return member

    async def update_member_with_image(
        self,
        member_id: int,
        name: str | None,
        rank: str | None,
        description: str | None,
        image_file: UploadFile | None,
        skills_json: str | None,
        links_json: str | None,
    ) -> Member:
        """
        Update member profile with optional image replacement.

        Args:
            member_id: Member ID to update
            name: New name (optional)
            rank: New rank (optional)
            description: New description (optional)
            image_file: New image file (optional)
            skills_json: JSON string of skills array (optional)
            links_json: JSON string of links array (optional)

        Returns:
            Updated member

        Raises:
            ValueError: If validation fails or member not found
            RuntimeError: If storage operation fails
        """
        member_repo = MemberRepository.create(self.db)
        member = member_repo.get_member_by_id(member_id)

        if not member:
            raise ValueError(f"Member not found: {member_id}")

        temp_file_path = None
        new_image_url = None

        try:
            # 1. 스킬/링크 JSON 파싱 (전달된 경우에만)
            skills_data = None
            links_data = None

            if skills_json is not None:
                try:
                    skills_data = json.loads(skills_json)
                except json.JSONDecodeError as e:
                    raise ValueError(f"Invalid JSON format for skills: {e}") from e

            if links_json is not None:
                try:
                    links_data = json.loads(links_json)
                except json.JSONDecodeError as e:
                    raise ValueError(f"Invalid JSON format for links: {e}") from e

            # 2. 새 이미지 업로드 (전달된 경우에만)
            if image_file:
                await FileValidationService.validate_profile_image(image_file)

                # 임시 파일 저장
                with tempfile.NamedTemporaryFile(delete=False, suffix=".tmp") as tmp:
                    content = await image_file.read()
                    tmp.write(content)
                    temp_file_path = tmp.name

                try:
                    new_image_url = await self.storage_service.upload_profile_image(
                        temp_file_path,
                        member_id,
                        image_file.filename or "profile.jpg",
                    )

                    # 3. 기존 이미지 안전하게 삭제 (S3 URL인 경우에만)
                    if member.image_url and self.storage_service.is_managed_url(member.image_url):
                        await self.storage_service.delete_profile_image(member.image_url)
                        logger.info(f"Deleted old profile image for member {member_id}")

                    member.image_url = new_image_url
                    logger.info(f"Uploaded new profile image for member {member_id}: {new_image_url}")

                except Exception as e:
                    logger.error(f"Failed to upload new profile image: {e}")
                    raise RuntimeError(f"Failed to upload profile image: {str(e)}") from e

            # 4. 기본 정보 업데이트 (전달된 필드만)
            if name is not None:
                member.name = name
            if rank is not None:
                member.rank = rank
            if description is not None:
                member.description = description

            # 5. 스킬 업데이트 (전달된 경우에만)
            if skills_data is not None:
                # 기존 스킬 삭제
                self.db.query(Skill).filter(Skill.member_id == member_id).delete()
                # 새 스킬 추가
                for skill_data in skills_data:
                    if isinstance(skill_data, dict) and "skill_name" in skill_data:
                        skill = Skill(member_id=member_id, skill_name=skill_data["skill_name"])
                        self.db.add(skill)

            # 6. 링크 업데이트 (전달된 경우에만)
            if links_data is not None:
                # 기존 링크 삭제
                self.db.query(Link).filter(Link.member_id == member_id).delete()
                # 새 링크 추가
                for link_data in links_data:
                    if isinstance(link_data, dict) and "link_type" in link_data and "url" in link_data:
                        link = Link(
                            member_id=member_id,
                            link_type=link_data["link_type"],
                            url=link_data["url"],
                        )
                        self.db.add(link)

            # 7. 커밋
            self.db.commit()
            self.db.refresh(member)

            logger.info(f"Member profile updated: {member.email}")
            return member

        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to update member profile: {e}")

            # 실패 시 업로드된 새 파일 삭제
            if new_image_url and temp_file_path and os.path.exists(temp_file_path):
                try:
                    os.unlink(temp_file_path)
                    logger.info(f"Cleaned up temporary file: {temp_file_path}")
                except Exception as cleanup_error:
                    logger.error(f"Failed to clean up temporary file: {cleanup_error}")

            raise e

        finally:
            # 임시 파일 정리
            if temp_file_path and os.path.exists(temp_file_path):
                try:
                    os.unlink(temp_file_path)
                except Exception:
                    pass

    def update_member(self, member_id: int, update_data: MemberUpdate) -> Member:
        """Update member profile"""
        member_repo = MemberRepository.create(self.db)
        member = member_repo.get_member_by_id(member_id)

        if not member:
            raise ValueError(f"Member with ID {member_id} not found")

        updated_member = member_repo.update_member(member, update_data)
        logger.info(f"Member profile updated: {member.email}")
        return updated_member

    def get_member_by_id(self, member_id: int) -> Member | None:
        """Get member by ID"""
        member_repo = MemberRepository.create(self.db)
        return member_repo.get_member_by_id(member_id)

    def get_member_by_email(self, email: str) -> Member | None:
        """Get member by email"""
        member_repo = MemberRepository.create(self.db)
        return member_repo.get_member_by_email(email)

    def get_all_members(self, status: MemberStatus | None = None) -> list[Member]:
        """Get all members, optionally filtered by status"""
        member_repo = MemberRepository.create(self.db)
        return member_repo.get_all_members(status)

    def approve_member(self, member_id: int) -> Member:
        """Approve a member registration (admin only): PENDING → APPROVED"""
        member_repo = MemberRepository.create(self.db)
        member = member_repo.get_member_by_id(member_id)

        if not member:
            raise ValueError(f"Member with ID {member_id} not found")

        if member.status != MemberStatus.PENDING:
            raise ValueError(
                f"Cannot approve member with status {member.status.value}. "
                "Only PENDING members can be approved."
            )

        # Update status to APPROVED
        member = member_repo.update_member_status(member, MemberStatus.APPROVED)

        # Send approval notification
        self.email_service.send_approval_notification(member.email, member.name)
        logger.info(f"Member approved: {member.email}")

        return member

    def reject_member(self, member_id: int) -> None:
        """Reject a member registration (admin only): Delete from DB"""
        member_repo = MemberRepository.create(self.db)
        member = member_repo.get_member_by_id(member_id)

        if not member:
            raise ValueError(f"Member with ID {member_id} not found")

        # Store email for logging before deletion
        email = member.email

        # Delete member from DB
        member_repo.delete_member(member)
        logger.info(f"Member rejected and deleted: {email}")

    def delete_member(self, member_id: int) -> None:
        """Delete a member"""
        member_repo = MemberRepository.create(self.db)
        member = member_repo.get_member_by_id(member_id)

        if not member:
            raise ValueError(f"Member with ID {member_id} not found")

        member_repo.delete_member(member)
        logger.info(f"Member deleted: {member.email}")
