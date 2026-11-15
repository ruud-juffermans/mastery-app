
import ast
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SKIP = {".venv", "__pycache__"}


def imported_modules(path: Path) -> set[str]:
    """Every module name a file imports, read from the syntax tree, not the text."""
    names: set[str] = set()
    for node in ast.walk(ast.parse(path.read_text())):
        if isinstance(node, ast.Import):
            names.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module and node.level == 0:
            names.add(node.module)
    return names


def offenders(package: str, forbidden: str) -> list[str]:
    found = []
    for path in sorted((ROOT / package).rglob("*.py")):
        if SKIP.intersection(path.parts):
            continue
        for name in imported_modules(path):
            if name == forbidden or name.startswith(forbidden + "."):
                found.append(f"{path.relative_to(ROOT)} imports {name}")
    return found


@pytest.mark.parametrize(
    ("package", "forbidden"),
    [("api", "worker"), ("worker", "api")],
)
def test_packages_do_not_import_each_other(package, forbidden):
    assert offenders(package, forbidden) == []
