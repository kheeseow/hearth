import ast
import re
from pathlib import Path

REPO_ROOT = Path(__file__).parents[2]
BACKEND_ROOT = REPO_ROOT / "mealie"
FRONTEND_ROOT = REPO_ROOT / "frontend" / "app"
FRONTEND_IMPORT_PATTERN = re.compile(
    r"\bfrom\s+[\"']([^\"']+)[\"']|^\s*import\s+[\"']([^\"']+)[\"']|\bimport\s*\(\s*[\"']([^\"']+)[\"']",
    re.MULTILINE,
)


def _is_guide_file(path: Path, root: Path) -> bool:
    return any("guide" in part.casefold() for part in path.relative_to(root).parts)


def _is_recipe_module(module: str) -> bool:
    return any(part.startswith("recipe") for part in re.split(r"[./_-]+", module.casefold()))


def _backend_violations() -> list[str]:
    violations: list[str] = []
    for path in sorted(BACKEND_ROOT.rglob("*.py")):
        if not _is_guide_file(path, BACKEND_ROOT):
            continue

        tree = ast.parse(path.read_text(), filename=str(path))
        for node in ast.walk(tree):
            imported: list[str] = []
            if isinstance(node, ast.Import):
                imported = [alias.name for alias in node.names]
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported = [node.module, *(alias.name for alias in node.names)]

            recipe_import = next((module for module in imported if _is_recipe_module(module)), None)
            if recipe_import:
                violations.append(f"{path.relative_to(REPO_ROOT)}:{node.lineno}: {recipe_import}")

    return violations


def _frontend_violations() -> list[str]:
    violations: list[str] = []
    for path in sorted(FRONTEND_ROOT.rglob("*")):
        if path.suffix not in {".ts", ".vue"} or ".test." in path.name or "__tests__" in path.parts:
            continue
        if not _is_guide_file(path, FRONTEND_ROOT):
            continue

        source = path.read_text()
        for match in FRONTEND_IMPORT_PATTERN.finditer(source):
            module = next(group for group in match.groups() if group is not None)
            if _is_recipe_module(module):
                line = source.count("\n", 0, match.start()) + 1
                violations.append(f"{path.relative_to(REPO_ROOT)}:{line}: {module}")

    return violations


def test_guide_backend_has_no_recipe_domain_imports() -> None:
    violations = _backend_violations()
    assert violations == [], "Guide backend imports Recipe-domain code:\n" + "\n".join(violations)


def test_guide_frontend_has_no_recipe_domain_imports() -> None:
    violations = _frontend_violations()
    assert violations == [], "Guide frontend imports Recipe-domain code:\n" + "\n".join(violations)
