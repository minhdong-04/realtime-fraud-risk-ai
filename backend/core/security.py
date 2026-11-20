"""Password hashing and JWT validation used by authenticated boundaries."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

import bcrypt
import jwt

from backend.core.settings import Settings, get_settings


class TokenValidationError(ValueError):
    """Raised when a JWT cannot prove an authenticated identity."""


@dataclass(frozen=True, slots=True)
class TokenClaims:
    """Normalized identity claims accepted by application dependencies."""

    subject: str
    role: str
    expires_at: datetime


def hash_password(password: str) -> str:
    """
    {
        func   : hash_password
        desc   : Băm mật khẩu bằng bcrypt trước khi lưu trữ.
        input  : password (str) — mật khẩu thô không rỗng.
        output : str — bcrypt hash đã mã hóa.
        loop   : 0 loops.
        throws : ValueError — khi mật khẩu trống.
    }
    """
    if not password:
        raise ValueError("Password is required")
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, encoded_password: str) -> bool:
    """
    {
        func   : verify_password
        desc   : So sánh mật khẩu thô với bcrypt hash đã lưu.
        input  : password (str), encoded_password (str) — giá trị xác thực.
        output : bool — true khi mật khẩu khớp.
        loop   : 0 loops.
    }
    """
    if not password or not encoded_password:
        return False
    try:
        return bcrypt.checkpw(password.encode("utf-8"), encoded_password.encode("utf-8"))
    except ValueError:  # hash lưu trữ không phải bcrypt hợp lệ → coi như sai mật khẩu
        return False


def create_access_token(
    subject: str,
    role: str,
    settings: Settings,
    now: datetime | None = None,
    expires_delta: timedelta | None = None,
) -> str:
    """
    {
        func   : create_access_token
        desc   : Ký JWT chứa danh tính và role cho phiên đăng nhập.
        input  : subject (str), role (str), settings (Settings), now (datetime | None).
        output : str — JWT đã ký.
        loop   : 0 loops.
    }
    """
    issued_at = now or datetime.now(UTC)
    expires_at = issued_at + (expires_delta or timedelta(minutes=settings.access_token_minutes))
    payload = {
        "sub": subject,
        "role": role,
        "iss": settings.jwt_issuer,
        "aud": settings.jwt_audience,
        "iat": issued_at,
        "exp": expires_at,
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def create_jwt_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """
    {
        func   : create_jwt_token
        desc   : Tạo JWT token nhanh từ payload dictionary phục vụ kiểm thử và xác thực
        input  : data (dict), expires_delta (timedelta | None)
        output : str — JWT token đã ký
        loop   : 0 loops
    }
    """
    to_encode = data.copy()
    expire = datetime.now(UTC) + (expires_delta or timedelta(hours=24))
    to_encode.update({"exp": expire})
    curr_settings = get_settings()
    return jwt.encode(to_encode, curr_settings.jwt_secret, algorithm=curr_settings.jwt_algorithm)


def decode_access_token(token: str, settings: Settings) -> TokenClaims:
    """
    {
        func   : decode_access_token
        desc   : Xác minh chữ ký, issuer, audience và hạn JWT.
        input  : token (str) — bearer token, settings (Settings) — khóa xác minh.
        output : TokenClaims — danh tính đã xác thực.
        loop   : 0 loops.
        throws : TokenValidationError — khi token không hợp lệ.
    }
    """
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret,
            algorithms=[settings.jwt_algorithm],
            issuer=settings.jwt_issuer,
            audience=settings.jwt_audience,
        )
    except jwt.PyJWTError as error:
        raise TokenValidationError("Invalid access token") from error

    subject = payload.get("sub")
    role = payload.get("role")
    expires_at = payload.get("exp")
    if not isinstance(subject, str) or not isinstance(role, str) or not isinstance(expires_at, (int, float)):
        raise TokenValidationError("Access token is missing required claims")
    return TokenClaims(subject=subject, role=role, expires_at=datetime.fromtimestamp(expires_at, UTC))
