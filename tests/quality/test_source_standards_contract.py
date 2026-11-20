"""Behavior tests for the source-quality guard."""

from scripts.check_code_standards import inspect_path


def test_source_guard_flags_files_at_the_300_line_limit(tmp_path) -> None:
    """Reject code files that are not strictly below the 300-line threshold."""
    source = tmp_path / "too_long.py"
    source.write_text("\n".join("pass" for _ in range(300)), encoding="utf-8")

    violations = inspect_path(tmp_path)

    assert any("must stay below 300 lines" in item.message for item in violations)


def test_source_guard_requires_a_public_python_docstring(tmp_path) -> None:
    """Reject public Python functions that lack a concise function purpose."""
    source = tmp_path / "undocumented.py"
    source.write_text("def calculate_risk():\n    return 1\n", encoding="utf-8")

    violations = inspect_path(tmp_path)

    assert any("public function needs a docstring" in item.message for item in violations)


def test_source_guard_ignores_generated_dependency_directories(tmp_path) -> None:
    """Exclude generated dependency bundles from project source standards."""
    generated = tmp_path / "node_modules"
    generated.mkdir()
    (generated / "bundle.ts").write_text("\n".join("export {}" for _ in range(350)), encoding="utf-8")

    assert inspect_path(tmp_path) == []
