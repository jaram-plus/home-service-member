import logging
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import model_validator

logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # Environment
    app_env: str = "development"  # development, testing, production

    # Database
    database_url: str = "sqlite:////app/data/jaram.db"

    # JWT
    jwt_secret_key: str = "change-this-secret-key-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expiration_minutes: int = 30

    # S3 Compatible Storage (MinIO dev / Cloudflare R2 prod)
    storage_endpoint_url: str = "http://minio:9000"
    storage_access_key_id: str = "minioadmin"
    storage_secret_access_key: str = "minioadmin"
    storage_bucket_name: str = "jaram-profiles"
    storage_region: str = "us-east-1"
    storage_public_url: str = "https://images.jaram.net"

    # Cloudflare R2 (production only)
    r2_account_id: str | None = None
    r2_access_key_id: str | None = None
    r2_secret_access_key: str | None = None

    # CORS
    frontend_url: str = "http://localhost:3000"

    # Base URL for magic links (e.g., "https://api.example.com" or "http://localhost:8000")
    base_url: str = "http://api.jaram.net"

    # Email Service
    email_provider: str = "mock"  # "mock" or "resend"
    resend_api_key: str | None = None
    email_from: str = "Jaram <team@jaram.net>"

    # Admin
    admin_internal_key: str = "dev-admin-key-change-in-production"

    @model_validator(mode="after")
    def validate_production_settings(self) -> "Settings":
        """Validate critical settings for production environment."""
        if self.app_env.lower() == "production":
            default_key = "change-this-secret-key-in-production"
            default_admin_key = "dev-admin-key-change-in-production"

            if self.jwt_secret_key == default_key or not self.jwt_secret_key.strip():
                error_msg = (
                    "SECURITY ERROR: JWT_SECRET_KEY must be set to a secure, "
                    "unique value in production. "
                    f"Current value: '{self.jwt_secret_key}'. "
                    "Please set JWT_SECRET_KEY environment variable with a strong secret."
                )
                logger.error(error_msg)
                raise RuntimeError(error_msg)

            if self.admin_internal_key == default_admin_key or not self.admin_internal_key.strip():
                error_msg = (
                    "SECURITY ERROR: ADMIN_INTERNAL_KEY must be set to a secure, "
                    "unique value in production. "
                    "Please set ADMIN_INTERNAL_KEY environment variable with a strong secret."
                )
                logger.error(error_msg)
                raise RuntimeError(error_msg)

        # Validate Resend API key when using Resend provider
        if self.email_provider.lower() == "resend":
            if not self.resend_api_key or not self.resend_api_key.strip():
                error_msg = (
                    "CONFIGURATION ERROR: RESEND_API_KEY must be set when EMAIL_PROVIDER is 'resend'. "
                    "Please set RESEND_API_KEY environment variable with your Resend API key."
                )
                logger.error(error_msg)
                raise RuntimeError(error_msg)

        return self


settings = Settings()
