"""TOTP (Time-based OTP) utilities for admin authentication."""

import os

import pyotp

# Fixed TOTP secret from environment (generate with: pyotp.random_base32())
TOTP_SECRET = os.getenv("ADMIN_TOTP_SECRET", "JARAM4MIN4DMIN4DMIN4MIN4MIN4===")


def get_totp() -> pyotp.TOTP:
    """Get TOTP instance with fixed secret."""
    return pyotp.TOTP(TOTP_SECRET, digits=6, interval=30)


def verify_totp(code: str) -> bool:
    """
    Verify TOTP code.

    Args:
        code: 6-digit OTP code

    Returns:
        True if code is valid (within 1 window before/after for clock skew)
    """
    totp = get_totp()
    return totp.verify(code, valid_window=1)


def get_provisioning_uri() -> str:
    """
    Get provisioning URI for QR code (Google Authenticator etc).

    Returns:
        otpauth:// URI string
    """
    totp = get_totp()
    return totp.provisioning_uri(
        name="Jaram Admin",
        issuer_name="Jaram"
    )


def get_current_otp() -> str:
    """Get current TOTP code (for testing)."""
    return get_totp().now()
