"""Contract tests for pytest temporary directories."""

from scripts.check_code_standards import inspect_path


def test_source_guard_ignores_pytest_temp_directories(tmp_path) -> None:
    """Exclude pytest temporary files before UTF-8 source inspection."""
    generated = tmp_path / ".pytest-tmp"
    generated.mkdir()
    (generated / "legacy.py").write_bytes(b"# -*- coding: big5 -*-\n\xa4@\n")

    assert inspect_path(tmp_path) == []
