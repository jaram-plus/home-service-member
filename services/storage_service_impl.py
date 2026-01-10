"""S3-compatible storage service implementation using boto3."""

import logging
from pathlib import Path
from urllib.parse import urlparse

import boto3
from botocore.exceptions import ClientError

from config import settings
from services.storage_service import StorageService

logger = logging.getLogger(__name__)


class S3StorageService(StorageService):
    """S3-compatible storage service using boto3."""

    def __init__(self):
        """Initialize S3 client with configuration."""
        self.s3_client = boto3.client(
            "s3",
            endpoint_url=settings.storage_endpoint_url,
            aws_access_key_id=settings.storage_access_key_id,
            aws_secret_access_key=settings.storage_secret_access_key,
            region_name=settings.storage_region,
        )
        self.bucket_name = settings.storage_bucket_name
        self.public_url = settings.storage_public_url
        logger.info(f"S3StorageService initialized: endpoint={settings.storage_endpoint_url}, bucket={self.bucket_name}")

    async def upload_profile_image(
        self,
        file_path: str,
        member_id: int,
        filename: str,
    ) -> str:
        """
        Upload profile image to S3-compatible storage.

        Args:
            file_path: Path to temporary file
            member_id: Member ID for path generation
            filename: Original filename

        Returns:
            Public URL of uploaded file

        Raises:
            RuntimeError: If upload fails
        """
        # 안전한 파일명 생성 (member_id 기반 경로)
        safe_filename = self._sanitize_filename(filename)
        s3_key = f"profiles/{member_id}/{safe_filename}"

        try:
            # S3 업로드
            self.s3_client.upload_file(
                file_path,
                self.bucket_name,
                s3_key,
                ExtraArgs={"ContentType": self._get_content_type(filename)},
            )

            # 공개 URL 생성
            public_url = f"{self.public_url}/{s3_key}"
            logger.info(f"Uploaded profile image: {s3_key} -> {public_url}")

            return public_url

        except ClientError as e:
            logger.error(f"Failed to upload file to S3: {e}")
            raise RuntimeError(f"Storage upload failed: {str(e)}") from e
        except Exception as e:
            logger.error(f"Unexpected error during file upload: {e}")
            raise RuntimeError(f"Storage upload failed: {str(e)}") from e

    async def delete_profile_image(self, image_url: str) -> None:
        """
        Delete profile image from S3-compatible storage.

        Only deletes if the URL is managed by this service (S3 URL).
        External URLs are ignored.

        Args:
            image_url: URL of image to delete
        """
        # S3 관리 URL인지 확인
        if not self.is_managed_url(image_url):
            logger.info(f"Skipping deletion of non-managed URL: {image_url}")
            return

        s3_key = self._url_to_key(image_url)
        if not s3_key:
            logger.warning(f"Could not extract S3 key from URL: {image_url}")
            return

        try:
            self.s3_client.delete_object(Bucket=self.bucket_name, Key=s3_key)
            logger.info(f"Deleted profile image from S3: {s3_key}")

        except ClientError as e:
            # 삭제 실패 시에도 로그만 남기고 계속 진행 (롤백 방지)
            logger.error(f"Failed to delete file from S3: {e}")
        except Exception as e:
            logger.error(f"Unexpected error during file deletion: {e}")

    def is_managed_url(self, image_url: str) -> bool:
        """
        Check if URL is managed by this storage service.

        Args:
            image_url: URL to check

        Returns:
            True if URL is managed by this service, False otherwise
        """
        if not image_url:
            return False

        # 1. 공개 URL 도메인 확인
        if not image_url.startswith(self.public_url):
            return False

        # 2. 경로 패턴 확인 (profiles/{member_id}/)
        try:
            path = urlparse(image_url).path
            # path는 /profiles/123/filename.jpg 형식이어야 함
            return path.startswith("/profiles/") and len(path.split("/")) >= 3
        except Exception:
            return False

    def extract_member_id(self, image_url: str) -> int | None:
        """
        Extract member ID from image URL.

        Args:
            image_url: URL to extract from

        Returns:
            Member ID or None if not found
        """
        s3_key = self._url_to_key(image_url)
        if not s3_key:
            return None

        # profiles/{member_id}/{filename} 형식에서 추출
        parts = s3_key.split("/")
        if len(parts) >= 2 and parts[0] == "profiles":
            try:
                return int(parts[1])
            except (ValueError, IndexError):
                return None

        return None

    @staticmethod
    def _url_to_key(image_url: str) -> str | None:
        """
        Convert public URL to S3 key.

        Args:
            image_url: Public URL

        Returns:
            S3 key or None if conversion fails
        """
        try:
            parsed = urlparse(image_url)
            # /profiles/{member_id}/{filename} 추출
            path = parsed.path
            if path.startswith("/"):
                path = path[1:]
            return path
        except Exception:
            return None

    @staticmethod
    def _sanitize_filename(filename: str) -> str:
        """
        Sanitize filename by removing dangerous characters.

        Args:
            filename: Original filename

        Returns:
            Sanitized filename
        """
        name = Path(filename).name
        # 알파벳, 숫자, 점, 하이픈, 언더스코어만 허용
        safe = "".join(c if c.isalnum() or c in ".-_" else "_" for c in name)
        return safe

    @staticmethod
    def _get_content_type(filename: str) -> str:
        """
        Get MIME type from filename.

        Args:
            filename: Filename

        Returns:
            MIME type string
        """
        ext = Path(filename).suffix.lower()
        mime_types = {
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".png": "image/png",
            ".webp": "image/webp",
            ".gif": "image/gif",
        }
        return mime_types.get(ext, "image/jpeg")


def create_storage_service() -> StorageService:
    """
    Factory function to create storage service.

    Returns:
        StorageService instance
    """
    return S3StorageService()
