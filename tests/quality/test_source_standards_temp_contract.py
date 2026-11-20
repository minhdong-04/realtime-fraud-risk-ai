"""Contract tests for transient test directories."""

from scripts.check_code_standards import inspect_path


def test_source_guard_ignores_codex_pytest_directories(tmp_path) -> None:
    """Exclude Codex-owned pytest fixtures from source-standard checks."""
    generated = tmp_path / ".codex-pytest-run"
    generated.mkdir()
    (generated / "fixture.py").write_text(
        "\n".join("pass" for _ in range(300)), encoding="utf-8"
    )

    assert inspect_path(tmp_path) == []
