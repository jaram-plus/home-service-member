"""Storage service abstraction for S3-compatible storage."""

from abc import ABC, abstractmethod


class StorageService(ABC):
    """Abstract storage service for S3-compatible storage."""

    @abstractmethod
    async def upload_profile_image(
        self,
        file_path: str,
        member_id: int,
        filename: str,
    ) -> str:
        """
        Upload profile image to storage.

        Args:
            file_path: Path to temporary file
            member_id: Member ID for path generation
            filename: Original filename

        Returns:
            Public URL of uploaded file

        Raises:
            RuntimeError: If upload fails
        """
        pass

    @abstractmethod
    async def delete_profile_image(self, image_url: str) -> None:
        """
        Delete profile image from storage.

        Only deletes if the URL is managed by this service (S3 URL).
        External URLs are ignored.

        Args:
            image_url: URL of image to delete
        """
        pass

    @abstractmethod
    def is_managed_url(self, image_url: str) -> bool:
        """
        Check if URL is managed by this storage service.

        Args:
            image_url: URL to check

        Returns:
            True if URL is managed by this service, False otherwise
        """
        pass

    @abstractmethod
    def extract_member_id(self, image_url: str) -> int | None:
        """
        Extract member ID from image URL.

        Args:
            image_url: URL to extract from

        Returns:
            Member ID or None if not found
        """
        pass
