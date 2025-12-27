from abc import ABC, abstractmethod


class EmailService(ABC):
    """Abstract email service for sending magic links and notifications"""

    @abstractmethod
    def send_magic_link(self, email: str, magic_link_url: str) -> None:
        """Send magic link email for authentication"""
        pass

    @abstractmethod
    def send_approval_notification(self, email: str, member_name: str) -> None:
        """Send approval notification email"""
        pass

    @abstractmethod
    def send_rejection_notification(self, email: str, member_name: str) -> None:
        """Send rejection notification email"""
        pass
