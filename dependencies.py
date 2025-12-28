"""FastAPI dependencies for authentication and authorization."""

from fastapi import Header, HTTPException

from config import settings


async def require_internal_admin(x_admin_key: str = Header(...)) -> bool:
    """
    Require internal admin API key for admin-only endpoints.

    This dependency validates that requests from admin frontends include
    the correct admin API key in the X-Admin-Key header.

    The admin frontend should read ADMIN_API_KEY from environment and
    include it in every request to protected endpoints.

    Args:
        x_admin_key: The admin API key from X-Admin-Key header

    Returns:
        True if authentication succeeds

    Raises:
        HTTPException: 403 if the key is invalid
    """
    if x_admin_key != settings.admin_internal_key:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid admin API key"
        )
    return True