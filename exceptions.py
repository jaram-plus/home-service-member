"""Custom exception classes for member service."""


class MemberServiceError(Exception):
    """Base exception for member service errors."""
    pass


class MemberNotFoundError(MemberServiceError):
    """Raised when a member is not found in the database."""
    pass


class MemberNotApprovedError(MemberServiceError):
    """Raised when a member is not in APPROVED status."""
    pass


class TokenMemberMismatchError(MemberServiceError):
    """Raised when the token doesn't match the requested member ID."""
    pass


class InvalidTokenError(MemberServiceError):
    """Raised when a token is invalid or expired."""
    pass
