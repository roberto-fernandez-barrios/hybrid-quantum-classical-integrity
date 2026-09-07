from pathlib import Path


def export_scripts_to_txt(src_dir: Path, out_file: Path) -> None:
    """
    Read all .py files recursively from src_dir and export them into a single TXT file.

    Excludes:
        - __pycache__ directories
    """

    py_files = sorted(
        p for p in src_dir.rglob("*.py")
        if "__pycache__" not in p.parts
    )

    if not py_files:
        raise SystemExit(f"No .py files found in {src_dir}")

    lines = []

    for file_path in py_files:
        try:
            content = file_path.read_text(encoding="utf-8")
        except Exception as e:
            content = f"[ERROR READING FILE: {e}]"

        lines.append(f"{file_path.relative_to(src_dir)}")
        lines.append("Código:")
        lines.append(content)
        lines.append("\n" + "-" * 60 + "\n")

    out_file.write_text("\n".join(lines), encoding="utf-8")

    print(f"[OK] Exported {len(py_files)} files → {out_file}")


def main():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--src", type=str, required=True,
                        help="Root directory (e.g. src)")
    parser.add_argument("--out", type=str, default="scripts_export.txt",
                        help="Output TXT file")

    args = parser.parse_args()

    src_dir = Path(args.src)
    out_file = Path(args.out)

    if not src_dir.exists():
        raise SystemExit(f"Source directory not found: {src_dir}")

    export_scripts_to_txt(src_dir, out_file)


if __name__ == "__main__":
    main()
