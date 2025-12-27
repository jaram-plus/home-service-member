import logging
from typing import Optional

import resend

from config import settings
from services.email_service import EmailService
from utils.jinja2 import render_template

logger = logging.getLogger(__name__)


class MockEmailService(EmailService):
    """Mock email service for development (logs to console)"""

    def send_magic_link(self, email: str, magic_link_url: str) -> None:
        """Send magic link email (logs to console in dev)"""
        html_content = render_template("magic_link.html", magic_link_url=magic_link_url)
        logger.info(f"[EMAIL] To: {email}")
        logger.info(f"[EMAIL] Subject: Jaram 이메일 인증")
        logger.info(f"[EMAIL] Magic Link URL: {magic_link_url}")
        logger.info(f"[EMAIL] HTML Content Length: {len(html_content)} chars")
        logger.debug(f"[EMAIL] HTML Preview:\n{html_content[:500]}...")

    def send_approval_notification(self, email: str, member_name: str) -> None:
        """Send approval notification email"""
        html_content = render_template("approval.html", member_name=member_name)
        logger.info(f"[EMAIL] To: {email}")
        logger.info(f"[EMAIL] Subject: Jaram 가입 승인 완료")
        logger.info(f"[EMAIL] Member Name: {member_name}")
        logger.info(f"[EMAIL] HTML Content Length: {len(html_content)} chars")
        logger.debug(f"[EMAIL] HTML Preview:\n{html_content[:500]}...")

    def send_rejection_notification(self, email: str, member_name: str) -> None:
        """Send rejection notification email"""
        html_content = render_template("rejection.html", member_name=member_name)
        logger.info(f"[EMAIL] To: {email}")
        logger.info(f"[EMAIL] Subject: Jaram 가입 신청 결과")
        logger.info(f"[EMAIL] Member Name: {member_name}")
        logger.info(f"[EMAIL] HTML Content Length: {len(html_content)} chars")
        logger.debug(f"[EMAIL] HTML Preview:\n{html_content[:500]}...")


class ResendEmailService(EmailService):
    """Resend를 사용한 이메일 서비스 구현"""

    DEFAULT_FROM_EMAIL = "Jaram <team@jaram.net>"

    def __init__(
        self,
        api_key: Optional[str] = None,
        from_email: Optional[str] = None,
    ):
        """
        ResendEmailService 초기화

        Args:
            api_key: Resend API 키 (None이면 환경변수 RESEND_API_KEY 사용)
            from_email: 발신자 이메일 주소
        """
        self.api_key = api_key or settings.resend_api_key
        if not self.api_key:
            raise ValueError("RESEND_API_KEY가 설정되지 않았습니다.")

        resend.api_key = self.api_key
        self.from_email = from_email or settings.email_from or self.DEFAULT_FROM_EMAIL

    def send_magic_link(self, email: str, magic_link_url: str) -> None:
        """Send magic link email for authentication"""
        html = render_template("magic_link.html", magic_link_url=magic_link_url)
        self._send(email, "Jaram 이메일 인증", html)

    def send_approval_notification(self, email: str, member_name: str) -> None:
        """Send approval notification email"""
        html = render_template("approval.html", member_name=member_name)
        self._send(email, "Jaram 가입 승인 완료", html)

    def send_rejection_notification(self, email: str, member_name: str) -> None:
        """Send rejection notification email"""
        html = render_template("rejection.html", member_name=member_name)
        self._send(email, "Jaram 가입 신청 결과", html)

    def _send(self, to: str, subject: str, html: str) -> None:
        """
        Resend API를 통해 이메일 발송

        Args:
            to: 수신자 이메일 주소
            subject: 이메일 제목
            html: 이메일 HTML 내용
        """
        params: resend.Emails.SendParams = {
            "from": self.from_email,
            "to": [to],
            "subject": subject,
            "html": html,
        }

        try:
            resend.Emails.send(params)
            logger.info(f"[EMAIL] Sent via Resend: to={to}, subject={subject}")
        except Exception as e:
            logger.error(f"[EMAIL] Failed to send via Resend: {e}")
            raise


def create_email_service() -> EmailService:
    """
    환경변수에 따라 이메일 서비스를 생성합니다.

    EMAIL_PROVIDER 환경변수:
        - "mock" 또는 설정되지 않음: MockEmailService (개발용)
        - "resend": ResendEmailService (실제 이메일 발송)

    Returns:
        EmailService 인스턴스
    """
    provider = (settings.email_provider or "mock").lower()

    if provider == "resend":
        logger.info("Email provider: Resend (실제 이메일 발송)")
        return ResendEmailService()
    else:
        logger.info("Email provider: Mock (로그만 출력)")
        return MockEmailService()
