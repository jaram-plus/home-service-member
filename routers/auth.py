import html
import logging

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

        # Validate and sanitize redirect URL to prevent open redirects
        allowed_origins = ["http://localhost:8501", "https://jaram.net"]
        if not any(redirect.startswith(origin) for origin in allowed_origins):
            redirect = "http://localhost:8501"  # Default to safe origin

        # Sanitize email to prevent XSS
        safe_email = html.escape(member.email)

        # Redirect to Streamlit frontend
        frontend_url = f"{redirect}?verified=true&email={safe_email}"
        safe_url = html.escape(frontend_url)

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta http-equiv="refresh" content="0;url={safe_url}">
            <script>
                window.location.href = "{safe_url}";
            </script>
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
        safe_redirect = html.escape(redirect)
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

        # Validate and sanitize redirect URL to prevent open redirects
        allowed_origins = ["http://localhost:8501", "https://jaram.net"]
        if not any(redirect.startswith(origin) for origin in allowed_origins):
            redirect = "http://localhost:8501"  # Default to safe origin

        # Sanitize token to prevent XSS (JWT tokens are URL-safe but escape for safety)
        safe_token = html.escape(token)

        # Redirect to Streamlit frontend with token query param
        # Streamlit MultiPage apps use query params to navigate, not URL paths
        frontend_url = f"{redirect}?token={safe_token}"
        safe_url = html.escape(frontend_url)

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta http-equiv="refresh" content="0;url={safe_url}">
            <script>
                window.location.href = "{safe_url}";
            </script>
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
        safe_redirect = html.escape(redirect)

        # Return error page
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
        status_code = 401
        if "Only approved members" in error_msg or "does not match" in error_msg:
            status_code = 403
        elif "not found" in error_msg.lower():
            status_code = 404
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
