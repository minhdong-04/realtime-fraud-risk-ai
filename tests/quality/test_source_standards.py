"""Regression test for the repository source-size rule."""

from pathlib import Path

from scripts.check_code_standards import inspect_path


def test_all_code_files_under_300_lines() -> None:
    """Keep every source file strictly below 300 physical lines."""
    root_dir = Path(__file__).resolve().parents[2]
    violations = [
        item
        for item in inspect_path(root_dir)
        if item.message == "source files must stay below 300 lines"
    ]

    assert not violations, f"Files at or above 300 lines: {violations}"