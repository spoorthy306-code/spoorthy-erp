from pathlib import Path


def fix_duplicate_imports(file_path: Path) -> None:
    """Remove exact duplicate import lines while preserving order."""
    content = file_path.read_text(encoding="utf-8")
    seen_imports = set()
    result_lines = []

    for line in content.splitlines():
        stripped = line.strip()
        is_import = stripped.startswith("import ") or stripped.startswith("from ")

        if is_import:
            if stripped in seen_imports:
                continue
            seen_imports.add(stripped)

        result_lines.append(line)

    file_path.write_text("\n".join(result_lines) + "\n", encoding="utf-8")
    print(f"fixed imports: {file_path}")


def main() -> None:
    root = Path(".")
    for py_file in root.rglob("*.py"):
        p = str(py_file)
        if any(skip in p for skip in [".venv", "venv", "site-packages", "__pycache__"]):
            continue
        fix_duplicate_imports(py_file)


if __name__ == "__main__":
    main()
