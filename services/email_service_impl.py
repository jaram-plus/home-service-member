import logging

from services.email_service import EmailService
from utils.email import get_approval_email_template, get_magic_link_email_template, get_rejection_email_template

logger = logging.getLogger(__name__)


class MockEmailService(EmailService):
    """Mock email service for development (logs to console)"""

    def send_magic_link(self, email: str, magic_link_url: str) -> None:
        """Send magic link email (logs to console in dev)"""
        html_content = get_magic_link_email_template(magic_link_url)
        logger.info(f"[EMAIL] To: {email}")
        logger.info(f"[EMAIL] Subject: JARAM 홈페이지 인증")
        logger.info(f"[EMAIL] Magic Link URL: {magic_link_url}")
        logger.info(f"[EMAIL] HTML Content Length: {len(html_content)} chars")
        # TODO: Integrate actual email API (AWS SES, SendGrid, etc.)

    def send_approval_notification(self, email: str, member_name: str) -> None:
        """Send approval notification email"""
        html_content = get_approval_email_template(member_name)
        logger.info(f"[EMAIL] To: {email}")
        logger.info(f"[EMAIL] Subject: 가입 승인 완료")
        logger.info(f"[EMAIL] HTML Content Length: {len(html_content)} chars")
        # TODO: Integrate actual email API

    def send_rejection_notification(self, email: str, member_name: str) -> None:
        """Send rejection notification email"""
        html_content = get_rejection_email_template(member_name)
        logger.info(f"[EMAIL] To: {email}")
        logger.info(f"[EMAIL] Subject: 가입 신청 결과")
        logger.info(f"[EMAIL] HTML Content Length: {len(html_content)} chars")
        # TODO: Integrate actual email API
