"""Runtime configuration with explicit safe defaults for local development."""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Mapping


class SettingsValidationError(ValueError):
    """Raised when an environment lacks required operational settings."""


@dataclass(frozen=True, slots=True)
class Settings:
    """Typed settings consumed by API, workers, and infrastructure adapters."""

    app_env: str
    database_url: str
    redis_url: str
    kafka_bootstrap_servers: str
    jwt_secret: str
    jwt_issuer: str
    jwt_audience: str
    jwt_algorithm: str
    access_token_minutes: int
    internal_api_key: str
    br03_default_limit: int
    psi_alert_threshold: float
    audit_retention_days: int
    alert_webhook_url: str | None
    allowed_origins: tuple[str, ...]

    @property
    def SECRET_KEY(self) -> str:
        """Alias cho jwt_secret"""
        return self.jwt_secret

    @property
    def ALGORITHM(self) -> str:
        """Alias cho jwt_algorithm"""
        return self.jwt_algorithm

    @classmethod
    def from_mapping(cls, values: Mapping[str, str] | None = None) -> "Settings":
        """
        {
            func   : from_mapping
            desc   : Đọc cấu hình môi trường và kiểm tra secret bắt buộc.
            input  : values (Mapping[str, str] | None) — giá trị ghi đè cho runtime/test.
            output : Settings — cấu hình đã chuẩn hóa.
            loop   : 0 loops.
            throws : SettingsValidationError — khi môi trường không đủ secret an toàn.
        }
        """
        source = dict(os.environ)
        source.update(values or {})
        app_env = source.get("APP_ENV", "development").lower()
        jwt_secret = source.get("JWT_SECRET") or "development-only-change-me"
        internal_api_key = source.get("INTERNAL_API_KEY") or "development-internal-key"
        if app_env in {"staging", "production"}:
            cls._require_production_secrets(source, jwt_secret, internal_api_key)

        redis_host = source.get("REDIS_HOST", "localhost")
        redis_port = cls._read_int(source, "REDIS_PORT", 6379)
        origins = tuple(filter(None, source.get("ALLOWED_ORIGINS", "http://localhost:3000").split(",")))
        return cls(
            app_env=app_env,
            database_url=source.get("DATABASE_URL", "sqlite:///./fraud_platform.db"),
            redis_url=source.get("REDIS_URL", f"redis://{redis_host}:{redis_port}/0"),
            kafka_bootstrap_servers=source.get("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092"),
            jwt_secret=jwt_secret,
            jwt_issuer=source.get("JWT_ISSUER", "sentinel-risk"),
            jwt_audience=source.get("JWT_AUDIENCE", "sentinel-risk-dashboard"),
            jwt_algorithm=source.get("JWT_ALGORITHM", "HS256"),
            access_token_minutes=cls._read_int(source, "ACCESS_TOKEN_MINUTES", 60),
            internal_api_key=internal_api_key,
            br03_default_limit=cls._read_int(source, "BR03_DEFAULT_LIMIT", 10_000_000),
            psi_alert_threshold=cls._read_float(source, "PSI_ALERT_THRESHOLD", 0.2),
            audit_retention_days=cls._read_int(source, "AUDIT_RETENTION_DAYS", 365),
            alert_webhook_url=source.get("ALERT_WEBHOOK_URL") or None,
            allowed_origins=origins,
        )

    @staticmethod
    def _require_production_secrets(
        source: Mapping[str, str], jwt_secret: str, internal_api_key: str
    ) -> None:
        missing = [
            name
            for name, value in {
                "JWT_SECRET": source.get("JWT_SECRET"),
                "INTERNAL_API_KEY": source.get("INTERNAL_API_KEY"),
            }.items()
            if not value
        ]
        if missing or jwt_secret.startswith("development-") or internal_api_key.startswith("development-"):
            raise SettingsValidationError("Production requires explicit JWT_SECRET and INTERNAL_API_KEY")

    @staticmethod
    def _read_int(source: Mapping[str, str], name: str, default: int) -> int:
        try:
            value = int(source.get(name, str(default)))
        except ValueError as error:
            raise SettingsValidationError(f"{name} must be an integer") from error
        if value <= 0:
            raise SettingsValidationError(f"{name} must be greater than zero")
        return value

    @staticmethod
    def _read_float(source: Mapping[str, str], name: str, default: float) -> float:
        try:
            value = float(source.get(name, str(default)))
        except ValueError as error:
            raise SettingsValidationError(f"{name} must be a number") from error
        if value <= 0:
            raise SettingsValidationError(f"{name} must be greater than zero")
        return value


def get_settings() -> Settings:
    """
    {
        func   : get_settings
        desc   : Tạo cấu hình runtime từ biến môi trường hiện tại.
        input  : None.
        output : Settings — cấu hình ứng dụng.
        loop   : 0 loops.
    }
    """
    return Settings.from_mapping()


settings = get_settings()
