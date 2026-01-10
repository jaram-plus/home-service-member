"""File validation service for profile image uploads."""

import logging
from pathlib import Path

from fastapi import UploadFile, HTTPException

logger = logging.getLogger(__name__)


class FileValidationService:
    """Service for validating uploaded profile images."""

    ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".gif"}
    ALLOWED_MIME_TYPES = {
        "image/jpeg",
        "image/png",
        "image/webp",
        "image/gif",
    }
    MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

    @classmethod
    async def validate_profile_image(cls, file: UploadFile | None) -> None:
        """
        Validate profile image file.

        Args:
            file: UploadFile object or None

        Raises:
            HTTPException: If validation fails
        """
        # 이미지는 선택사항이므로 None이면 통과
        if file is None:
            return

        # 1. 파일 크기 검증
        file.file.seek(0, 2)  # 끝으로 이동
        file_size = file.file.tell()
        file.file.seek(0)  # 다시 처음으로

        if file_size > cls.MAX_FILE_SIZE:
            raise HTTPException(
                status_code=413,
                detail=f"File size exceeds 5MB limit (got {file_size:,} bytes)",
            )

        if file_size == 0:
            raise HTTPException(
                status_code=400,
                detail="Empty file not allowed",
            )

        # 2. 파일 확장자 검증
        filename = file.filename or ""
        ext = Path(filename).suffix.lower()
        if ext not in cls.ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid file extension '{ext}'. Allowed: {', '.join(sorted(cls.ALLOWED_EXTENSIONS))}",
            )

        # 3. MIME 타입 검증
        content_type = file.content_type or ""
        if content_type not in cls.ALLOWED_MIME_TYPES:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid content type '{content_type}'. Allowed: {', '.join(sorted(cls.ALLOWED_MIME_TYPES))}",
            )

        # 4. 실제 파일 내용 검증 (magic bytes)
        header = await file.read(12)
        file.file.seek(0)

        if not cls._is_valid_image_header(header):
            logger.warning(f"Invalid image header for file: {filename}")
            raise HTTPException(
                status_code=400,
                detail="File content does not match its extension or is corrupted",
            )

        logger.info(f"File validation passed: {filename} ({file_size:,} bytes, {content_type})")

    @staticmethod
    def _is_valid_image_header(header: bytes) -> bool:
        """
        Validate image file using magic bytes.

        Args:
            header: First 8 bytes of file

        Returns:
            True if valid image header, False otherwise
        """
        if len(header) < 4:
            return False

        # JPEG: FF D8 FF
        if header[:3] == b"\xFF\xD8\xFF":
            return True

        # PNG: 89 50 4E 47 0D 0A 1A 0A
        if header[:8] == b"\x89\x50\x4E\x47\x0D\x0A\x1A\x0A":
            return True

        # GIF: 47 49 46 38 (GIF8)
        if header[:4] == b"GIF8":
            return True

        # WebP: RIFF....WEBP
        if len(header) >= 12 and header[:4] == b"RIFF" and header[8:12] == b"WEBP":
            return True

        return False
