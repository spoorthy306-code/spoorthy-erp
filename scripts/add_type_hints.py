import ast
from pathlib import Path


def report_missing_return_hints(file_path: Path) -> None:
    """Report functions that do not declare return type annotations."""
    try:
        source = file_path.read_text(encoding="utf-8")
        tree = ast.parse(source)
    except (SyntaxError, UnicodeDecodeError):
        return

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if node.returns is None:
                print(f"missing return type: {file_path}:{node.lineno} {node.name}")


def main() -> None:
    root = Path(".")
    for py_file in root.rglob("*.py"):
        p = str(py_file)
        if any(skip in p for skip in [".venv", "venv", "site-packages", "__pycache__"]):
            continue
        report_missing_return_hints(py_file)


if __name__ == "__main__":
    main()
