"""Validate source size, documentation, and loop constraints mechanically."""

from __future__ import annotations

import ast
import re
import sys
from dataclasses import dataclass
from pathlib import Path


MAX_LINES = 299
SOURCE_SUFFIXES = {".py", ".ts", ".tsx"}
IGNORED_DIRECTORIES = {".git", ".next", "__pycache__", "node_modules", ".pytest_cache", ".pytest-tmp", ".venv", "venv"}
LOOP_NODES = (ast.For, ast.AsyncFor, ast.While, ast.ListComp, ast.SetComp, ast.DictComp, ast.GeneratorExp)


@dataclass(frozen=True, slots=True)
class Violation:
    """A machine-readable source-standard finding."""

    path: Path
    line: int
    message: str


def inspect_path(path: Path) -> list[Violation]:
    """
    {
        func   : inspect_path
        desc   : Kiểm tra giới hạn dòng và tài liệu của source dưới một đường dẫn.
        input  : path (Path) — file hoặc thư mục cần quét.
        output : list[Violation] — lỗi tiêu chuẩn đã phát hiện.
        loop   : 1 loop — kiểm tra từng source file hợp lệ.
    }
    """
    violations: list[Violation] = []
    # { loop-1: áp dụng kiểm tra phù hợp cho từng file source }
    for source in _source_files(path):
        violations.extend(_inspect_file(source))
    return violations


def _source_files(path: Path) -> list[Path]:
    if path.is_file():
        return [path] if path.suffix in SOURCE_SUFFIXES else []
    return [item for item in path.rglob("*") if _is_source_file(item)]


def _is_source_file(path: Path) -> bool:
    return path.is_file() and path.suffix in SOURCE_SUFFIXES and not any(
        part in IGNORED_DIRECTORIES or part.startswith(".codex-pytest-") for part in path.parts
    )


def _inspect_file(path: Path) -> list[Violation]:
    text = path.read_text(encoding="utf-8")
    violations = _line_limit_violation(path, text)
    if path.suffix == ".py":
        violations.extend(_inspect_python(path, text))
    else:
        violations.extend(_inspect_typescript(path, text))
    return violations


def _line_limit_violation(path: Path, text: str) -> list[Violation]:
    line_count = len(text.splitlines())
    if line_count <= MAX_LINES:
        return []
    return [Violation(path, 1, "source files must stay below 300 lines")]


def _inspect_python(path: Path, text: str) -> list[Violation]:
    tree = ast.parse(text, filename=str(path))
    violations: list[Violation] = []
    # { loop-1: kiểm tra hàm public và giới hạn vòng lặp trong từng hàm }
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            violations.extend(_inspect_python_function(path, node))
    return violations


def _inspect_python_function(path: Path, node: ast.FunctionDef | ast.AsyncFunctionDef) -> list[Violation]:
    violations: list[Violation] = []
    if not node.name.startswith("_") and ast.get_docstring(node) is None:
        violations.append(Violation(path, node.lineno, "public function needs a docstring"))
    loop_count = sum(1 for child in ast.walk(node) if isinstance(child, LOOP_NODES))
    if loop_count > 2:
        violations.append(Violation(path, node.lineno, "functions may contain at most two loops"))
    return violations


def _inspect_typescript(path: Path, text: str) -> list[Violation]:
    violations: list[Violation] = []
    exported = re.finditer(r"^\\s*export\\s+(?:default\\s+)?(?:async\\s+)?(?:function|const|class)\\s+(\\w+)", text, re.MULTILINE)
    # { loop-1: xác minh export có JSDoc ngắn mô tả mục đích }
    for match in exported:
        before = text[: match.start()].rstrip()
        if not before.endswith("*/"):
            line = text.count("\n", 0, match.start()) + 1
            violations.append(Violation(path, line, "exported TypeScript code needs JSDoc"))
    return violations


def main() -> int:
    """
    {
        func   : main
        desc   : Chạy source-quality guard từ command line.
        input  : None.
        output : int — mã exit phù hợp với kết quả kiểm tra.
        loop   : 1 loop — in từng violation đã phát hiện.
    }
    """
    target = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(".")
    violations = inspect_path(target)
    # { loop-1: xuất lỗi theo định dạng dễ đọc cho CI }
    for item in violations:
        print(f"{item.path}:{item.line}: {item.message}")
    return 1 if violations else 0


if __name__ == "__main__":
    raise SystemExit(main())
