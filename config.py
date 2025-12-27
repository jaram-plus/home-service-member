from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # Database
    database_url: str = "sqlite:///./jaram.db"

    # JWT
    jwt_secret_key: str = "change-this-secret-key-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expiration_minutes: int = 30

    # MinIO (development)
    minio_endpoint: str = "localhost:9000"
    minio_access_key: str = "minioadmin"
    minio_secret_key: str = "minioadmin"
    minio_bucket_name: str = "jaram-profiles"
    minio_secure: bool = False

    # CORS
    frontend_url: str = "http://localhost:3000"

    # Base URL for magic links (e.g., "https://api.example.com" or "http://localhost:8000")
    base_url: str = "http://localhost:8000"


settings = Settings()
