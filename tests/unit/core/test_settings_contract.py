"""Contract tests for safe runtime settings."""

import pytest

from backend.core.settings import Settings, SettingsValidationError


def test_production_settings_require_explicit_secrets() -> None:
    """Reject production startup when signing credentials are not configured."""
    with pytest.raises(SettingsValidationError):
        Settings.from_mapping({"APP_ENV": "production"})


def test_settings_expose_configurable_risk_defaults() -> None:
    """Keep BR-03, PSI, and audit retention outside hidden source constants."""
    settings = Settings.from_mapping(
        {
            "BR03_DEFAULT_LIMIT": "12000000",
            "PSI_ALERT_THRESHOLD": "0.25",
            "AUDIT_RETENTION_DAYS": "400",
        }
    )

    assert settings.br03_default_limit == 12_000_000
    assert settings.psi_alert_threshold == 0.25
    assert settings.audit_retention_days == 400


def test_settings_keep_webhook_disabled_without_a_url() -> None:
    """Represent an unconfigured alert channel without a false delivery claim."""
    assert Settings.from_mapping({}).alert_webhook_url is None
