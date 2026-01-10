import logging
from urllib.parse import quote

from config import settings
from models.member import Member, MemberStatus
from repositories.member_repository import MemberRepository
from schemas.member import MemberCreate, MemberUpdate
from services.email_service import EmailService
from services.email_service_impl import create_email_service
from sqlalchemy.orm import Session
from utils.token import create_magic_link_token, verify_magic_link_token

logger = logging.getLogger(__name__)


class MemberService:
    def __init__(self, db: Session, email_service: EmailService | None = None):
        self.db = db
        self.email_service = email_service or create_email_service()

    @staticmethod
    def _build_magic_link_url(token: str, endpoint: str = "verify") -> str:
        """Build magic link URL using configurable base URL.

        Args:
            token: JWT token
            endpoint: Endpoint name ("verify" for registration, "verify-profile-update" for profile update)
        """
        base_url = settings.base_url.rstrip("/")
        encoded_token = quote(token, safe="")
        return f"{base_url}/auth/{endpoint}?token={encoded_token}"

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

    def request_profile_update(self, email: str) -> str:
        """Request to update profile by sending magic link"""
        member_repo = MemberRepository.create(self.db)
        member = member_repo.get_member_by_email(email)

        if not member:
            raise ValueError(f"Member with email {email} not found")

        # Send magic link for profile update
        token = create_magic_link_token(email, purpose="profile_update")
        magic_link_url = self._build_magic_link_url(token, endpoint="verify-profile-update")
        self.email_service.send_magic_link(email, magic_link_url)

        logger.info(f"Profile update requested for: {email}")
        return magic_link_url

    def verify_magic_link(self, token: str, purpose: str = "auth") -> str:
        """Verify magic link token and return email"""
        email = verify_magic_link_token(token, purpose)
        if not email:
            raise ValueError("Invalid or expired token")
        return email

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

    def verify_profile_update_token(self, token: str) -> Member:
        """Verify profile update token and return member data"""
        # 토큰 검증 (purpose="profile_update")
        email = verify_magic_link_token(token, purpose="profile_update")
        if not email:
            raise ValueError("Invalid or expired token")

        # 회원 조회
        member_repo = MemberRepository.create(self.db)
        member = member_repo.get_member_by_email(email)

        if not member:
            raise ValueError(f"Member with email {email} not found")

        # APPROVED 상태만 수정 가능
        if member.status != MemberStatus.APPROVED:
            raise ValueError(
                f"Only approved members can update profiles. Current status: {member.status.value}"
            )

        logger.info(f"Profile update token verified for: {email}")
        return member

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
