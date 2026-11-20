"""Contract tests for password and JWT boundaries."""

from datetime import UTC, datetime, timedelta

import pytest

from backend.core.security import (
    TokenValidationError,
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)
from backend.core.settings import Settings


def build_settings() -> Settings:
    """Create isolated signing settings for security tests."""
    return Settings.from_mapping(
        {
            "JWT_SECRET": "test-signing-secret-with-32-bytes-minimum",
            "JWT_ISSUER": "fraud-test",
            "JWT_AUDIENCE": "fraud-dashboard",
        }
    )


def test_password_hash_rejects_the_wrong_password() -> None:
    """Protect login verification with a one-way bcrypt hash."""
    encoded = hash_password("correct-password")

    assert verify_password("correct-password", encoded) is True
    assert verify_password("incorrect-password", encoded) is False


def test_access_token_preserves_authenticated_identity() -> None:
    """Round-trip signed identity and role claims across the JWT boundary."""
    settings = build_settings()
    token = create_access_token(
        subject="analyst@fraud.test",
        role="ANALYST",
        settings=settings,
        now=datetime.now(UTC),
    )

    claims = decode_access_token(token, settings=settings)

    assert claims.subject == "analyst@fraud.test"
    assert claims.role == "ANALYST"


def test_expired_access_token_is_rejected() -> None:
    """Reject a token after its configured expiry time has elapsed."""
    settings = build_settings()
    token = create_access_token(
        subject="analyst@fraud.test",
        role="ANALYST",
        settings=settings,
        now=datetime.now(UTC) - timedelta(hours=2),
        expires_delta=timedelta(minutes=1),
    )

    with pytest.raises(TokenValidationError):
        decode_access_token(token, settings=settings)
