"""Contract tests for virtual-environment directories."""

from scripts.check_code_standards import inspect_path


def test_source_guard_ignores_virtual_environment_directories(tmp_path) -> None:
    """Exclude vendored virtual-environment files from source inspection."""
    generated = tmp_path / ".venv" / "Lib"
    generated.mkdir(parents=True)
    (generated / "legacy.py").write_bytes(b"# -*- coding: big5 -*-\n\xa4@\n")

    assert inspect_path(tmp_path) == []
