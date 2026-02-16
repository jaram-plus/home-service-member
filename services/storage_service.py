"""Storage service for handling image uploads to MinIO."""

import io
import logging
import uuid
from pathlib import Path

from minio import Minio
from minio.error import S3Error

from config import settings

logger = logging.getLogger(__name__)

# Allowed image file extensions
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp"}

# Max file size: 5MB
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB in bytes


class StorageService:
    """Service for handling file storage operations with MinIO."""

    def __init__(self):
        """Initialize MinIO client with configuration from settings."""
        self.client = Minio(
            endpoint=settings.minio_endpoint,
            access_key=settings.minio_access_key,
            secret_key=settings.minio_secret_key,
            secure=settings.minio_secure,
        )
        self.bucket_name = settings.minio_bucket_name
        self._ensure_bucket_exists()

    def _ensure_bucket_exists(self) -> None:
        """Create the bucket if it doesn't exist."""
        try:
            if not self.client.bucket_exists(self.bucket_name):
                self.client.make_bucket(self.bucket_name)
                logger.info(f"Created MinIO bucket: {self.bucket_name}")
            else:
                logger.info(f"MinIO bucket already exists: {self.bucket_name}")
        except S3Error as e:
            logger.error(f"Failed to ensure bucket exists: {e}")
            raise

    def _validate_file(self, filename: str, file_size: int) -> None:
        """
        Validate file type and size.

        Args:
            filename: Name of the uploaded file
            file_size: Size of the uploaded file in bytes

        Raises:
            ValueError: If file type or size is invalid
        """
        # Check file extension
        file_ext = Path(filename).suffix.lower()
        if file_ext not in ALLOWED_EXTENSIONS:
            raise ValueError(
                f"Invalid file type. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}"
            )

        # Check file size
        if file_size > MAX_FILE_SIZE:
            raise ValueError(f"File too large. Maximum size: {MAX_FILE_SIZE / (1024 * 1024)}MB")

    def _generate_unique_filename(self, original_filename: str) -> str:
        """
        Generate a unique filename using UUID and original extension.

        Args:
            original_filename: Original filename of the uploaded file

        Returns:
            Unique filename in format: <uuid>.<extension>
        """
        file_ext = Path(original_filename).suffix.lower()
        unique_name = f"{uuid.uuid4()}{file_ext}"
        return unique_name

    def upload_image(self, file_data: bytes, filename: str, content_type: str) -> str:
        """
        Upload an image to MinIO storage.

        Args:
            file_data: Binary data of the file to upload
            filename: Original filename of the uploaded file
            content_type: MIME type of the file (e.g., 'image/jpeg')

        Returns:
            Public URL of the uploaded image

        Raises:
            ValueError: If file validation fails
            S3Error: If upload fails
        """
        # Validate file
        self._validate_file(filename, len(file_data))

        # Generate unique filename
        object_name = self._generate_unique_filename(filename)

        try:
            # Upload file to MinIO
            # MinIO requires a file-like object with read() method
            data_stream = io.BytesIO(file_data)
            self.client.put_object(
                bucket_name=self.bucket_name,
                object_name=object_name,
                data=data_stream,
                length=len(file_data),
                content_type=content_type,
            )
            logger.info(f"Uploaded image: {object_name} to bucket {self.bucket_name}")

            # Generate public URL using public endpoint
            # MinIO URL format: http://public_endpoint/bucket/objectname
            protocol = "https" if settings.minio_secure else "http"
            url = f"{protocol}://{settings.minio_public_endpoint}/{self.bucket_name}/{object_name}"
            return url

        except S3Error as e:
            logger.error(f"Failed to upload image: {e}")
            raise

    def delete_image(self, image_url: str) -> bool:
        """
        Delete an image from MinIO storage.

        Args:
            image_url: Public URL of the image to delete

        Returns:
            True if deletion was successful, False otherwise

        Raises:
            S3Error: If deletion fails
        """
        try:
            # Extract object name from URL
            # URL format: http://endpoint/bucket/objectname
            parts = image_url.split(f"/{self.bucket_name}/")
            if len(parts) != 2:
                logger.warning(f"Invalid image URL format: {image_url}")
                return False

            object_name = parts[1]

            # Delete object from MinIO
            self.client.remove_object(bucket_name=self.bucket_name, object_name=object_name)
            logger.info(f"Deleted image: {object_name} from bucket {self.bucket_name}")
            return True

        except S3Error as e:
            logger.error(f"Failed to delete image: {e}")
            return False
