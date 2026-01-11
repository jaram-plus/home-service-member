import html
import logging
import os
from urllib.parse import urlparse, urlunparse, urlencode, parse_qs

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database import get_db
from schemas.member import MagicLinkRequest, MemberResponse
from services.member_service import MemberService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["auth"])


class MagicLinkVerifyResponse(BaseModel):
    """Response model for magic link verification"""

    email: str
    message: str


def get_member_service(db: Session = Depends(get_db)) -> MemberService:
    """Dependency to get member service"""
    return MemberService(db)


def validate_redirect_url(redirect: str) -> str:
    """Validate and return safe redirect URL from whitelist."""
    # Safe default origin
    safe_default = "http://localhost:8501"

    # Read allowed origins from environment variable
    allowed_origins_str = os.environ.get(
        "ALLOWED_REDIRECT_ORIGINS",
        "http://localhost:8501,https://jaram.net"
    )
    allowed_origins = [origin.strip() for origin in allowed_origins_str.split(",") if origin.strip()]

    # Ensure we have at least one allowed origin
    if not allowed_origins:
        allowed_origins = [safe_default]

    # Parse the redirect URL
    parsed = urlparse(redirect)

    # Validate that the URL has both scheme and netloc
    if not parsed.scheme or not parsed.netloc:
        return safe_default

    # Check if origin is in whitelist
    origin = f"{parsed.scheme}://{parsed.netloc}"
    if origin not in allowed_origins:
        return allowed_origins[0]  # Return first allowed origin (safe_default if list was empty)

    return redirect


@router.post("/magic-link/profile-update")
def request_profile_update_link(
    request: MagicLinkRequest, service: MemberService = Depends(get_member_service)
):
    """Request magic link for profile update

    TODO: Fix token validation mismatch. service.request_profile_update() creates
    purpose="profile_update" tokens, but /auth/verify calls service.verify_email()
    which only validates purpose="registration" tokens. Need to either:
    1. Create a separate verify endpoint for profile updates, or
    2. Make verify_email() handle both registration and profile_update purposes
    """
    try:
        service.request_profile_update(request.email)
        return {"message": "Magic link sent to your email"}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e


@router.get("/verify", response_class=HTMLResponse)
def verify_magic_link(
    token: str = Query(...),
    redirect: str = Query("http://localhost:8501", description="Frontend URL to redirect to"),
    service: MemberService = Depends(get_member_service)
):
    """Verify magic link token and change status to PENDING"""
    try:
        member = service.verify_email(token)

        # Validate redirect URL (prevents open redirects)
        safe_redirect = validate_redirect_url(redirect)

        # Build URL with encoded email parameter (no HTML escaping yet)
        parsed_redirect = urlparse(safe_redirect)
        query_params = parse_qs(parsed_redirect.query)
        query_params['verified'] = ['true']
        query_params['email'] = [member.email]
        new_query = urlencode(query_params, doseq=True)

        safe_url_parsed = parsed_redirect._replace(query=new_query)
        frontend_url = urlunparse(safe_url_parsed)

        # Escape only once when inserting into HTML
        safe_url = html.escape(frontend_url)

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta http-equiv="refresh" content="0;url={safe_url}">
        </head>
        <body>
            <p>Email verified! Redirecting...</p>
            <p>If not redirected, <a href="{safe_url}">click here</a>.</p>
        </body>
        </html>
        """
        return HTMLResponse(content=html_content, status_code=200)
    except ValueError as e:
        safe_error = html.escape(str(e))
        safe_redirect = html.escape(validate_redirect_url(redirect))
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head><title>Error</title></head>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 50px auto; padding: 20px;">
            <h1>Authentication Error</h1>
            <p>{safe_error}</p>
            <p><a href="{safe_redirect}">Return to home</a></p>
        </body>
        </html>
        """
        return HTMLResponse(content=html_content, status_code=401)


@router.get("/verify-profile-update", response_class=HTMLResponse)
def verify_profile_update(
    token: str = Query(...),
    redirect: str = Query("http://localhost:8501", description="Frontend URL to redirect to"),
    service: MemberService = Depends(get_member_service)
):
    """Verify profile update token and redirect to frontend (for email links)"""
    try:
        # Verify token (member data used only for validation)
        _ = service.verify_profile_update_token(token)

        # Validate redirect URL (prevents open redirects)
        safe_redirect = validate_redirect_url(redirect)

        # Build URL with encoded token parameter (no HTML escaping yet)
        parsed_redirect = urlparse(safe_redirect)
        query_params = parse_qs(parsed_redirect.query)
        query_params['token'] = [token]
        new_query = urlencode(query_params, doseq=True)

        safe_url_parsed = parsed_redirect._replace(query=new_query)
        frontend_url = urlunparse(safe_url_parsed)

        # Escape only once when inserting into HTML
        safe_url = html.escape(frontend_url)

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta http-equiv="refresh" content="0;url={safe_url}">
        </head>
        <body>
            <p>Redirecting to profile update page...</p>
            <p>If not redirected, <a href="{safe_url}">click here</a>.</p>
        </body>
        </html>
        """
        return HTMLResponse(content=html_content, status_code=200)
    except ValueError as e:
        error_msg = str(e)
        safe_error = html.escape(error_msg)
        safe_redirect = html.escape(validate_redirect_url(redirect))

        # Classify error by message content (will be improved with specific exception types)
        status_code = 401
        if "Only approved members" in error_msg or "does not match" in error_msg:
            status_code = 403
        elif "not found" in error_msg.lower():
            status_code = 404

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head><title>Error</title></head>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 50px auto; padding: 20px;">
            <h1>Authentication Error</h1>
            <p>{safe_error}</p>
            <p><a href="{safe_redirect}">Return to home</a></p>
        </body>
        </html>
        """
        return HTMLResponse(content=html_content, status_code=status_code)


@router.get("/verify-profile-update-json", response_model=MemberResponse)
def verify_profile_update_json(
    token: str = Query(...),
    service: MemberService = Depends(get_member_service)
):
    """Verify profile update token and return member data (for frontend API calls)"""
    try:
        member = service.verify_profile_update_token(token)
        return member
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e)) from e
