from datetime import datetime, timedelta

from jose import JWTError, jwt

from config import settings


def create_magic_link_token(email: str, purpose: str = "auth") -> str:
    """Create JWT token for magic link authentication"""
    expire = datetime.utcnow() + timedelta(minutes=settings.jwt_expiration_minutes)
    payload = {"sub": email, "exp": expire, "purpose": purpose}
    encoded_jwt = jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)
    return encoded_jwt


def verify_magic_link_token(token: str, purpose: str = "auth") -> str | None:
    """Verify JWT token and return email if valid"""
    try:
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
        email: str = payload.get("sub")
        token_purpose: str = payload.get("purpose")

        if email is None or token_purpose != purpose:
            return None
        return email
    except JWTError:
        return None
