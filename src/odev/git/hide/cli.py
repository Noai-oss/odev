from __future__ import annotations

import argparse
from pathlib import Path

from ..core import GitError, git_path


def exclude_path() -> Path:
    return git_path("info/exclude")


def _read_lines(path: Path) -> list[str]:
    if not path.exists():
        return []
    return path.read_text(encoding="utf-8").splitlines()


def _write_lines(path: Path, lines: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    content = "\n".join(lines)
    if content:
        content += "\n"
    path.write_text(content, encoding="utf-8")


def list_patterns(*, include_comments: bool = False) -> list[str]:
    lines = _read_lines(exclude_path())
    if include_comments:
        return lines
    return [
        line for line in lines if line.strip() and not line.lstrip().startswith("#")
    ]


def add_patterns(patterns: list[str]) -> list[str]:
    path = exclude_path()
    lines = _read_lines(path)
    existing = set(lines)
    added: list[str] = []

    for pattern in patterns:
        value = pattern.strip()
        if not value or value in existing:
            continue
        lines.append(value)
        existing.add(value)
        added.append(value)

    if added:
        _write_lines(path, lines)
    return added


def remove_patterns(patterns: list[str]) -> list[str]:
    path = exclude_path()
    lines = _read_lines(path)
    targets = {pattern.strip() for pattern in patterns if pattern.strip()}
    removed: list[str] = []
    next_lines: list[str] = []

    for line in lines:
        if line in targets:
            removed.append(line)
            continue
        next_lines.append(line)

    if removed:
        _write_lines(path, next_lines)
    return removed


def main_impl() -> None:
    parser = argparse.ArgumentParser(description="Manage git local exclude patterns")
    subparsers = parser.add_subparsers(dest="command", required=True)

    list_parser = subparsers.add_parser(
        "list", aliases=["ls"], help="List current local exclude patterns"
    )
    list_parser.add_argument(
        "--all", "-a", action="store_true", help="Include comments and blank lines"
    )

    _ = subparsers.add_parser(
        "show", help="Show the full content of the local exclude file"
    )

    add_parser = subparsers.add_parser("add", help="Add new local exclude patterns")
    add_parser.add_argument("patterns", nargs="+", help="Patterns to add")

    remove_parser = subparsers.add_parser(
        "remove", aliases=["rm"], help="Remove local existing exclude patterns"
    )
    remove_parser.add_argument("patterns", nargs="+", help="Patterns to remove")

    path_parser = subparsers.add_parser(
        "path", help="Show the path to the local exclude file"
    )
    path_parser.add_argument(
        "--edit",
        "-e",
        type=str,
        help="Open the local exclude file in the given editor",
        required=False,
    )

    args = parser.parse_args()

    match args.command:
        case "list" | "ls":
            patterns = list_patterns(include_comments=args.all)
            for pattern in patterns:
                print(pattern)
        case "add":
            added = add_patterns(args.patterns)
            if added:
                print("Added patterns:")
                for pattern in added:
                    print(f"  {pattern}")
            else:
                print("No new patterns were added.")
        case "remove" | "rm":
            removed = remove_patterns(args.patterns)
            if removed:
                print("Removed patterns:")
                for pattern in removed:
                    print(f"  {pattern}")
            else:
                print("No matching patterns were found to remove.")
        case "path":
            if args.edit:
                import shutil
                import subprocess

                editor_path = shutil.which(args.edit)
                if not editor_path:
                    print(f"Editor '{args.edit}' not found in PATH.")
                    return
                print(f"Opening {exclude_path()} in editor '{args.edit}'...")
                subprocess.run([editor_path, str(exclude_path())])
                print("Done.")
            else:
                print(exclude_path())
        case _:
            print(f"Unknown command: {args.command}")


def main() -> None:
    try:
        main_impl()
    except GitError as exc:
        print(f"[git-hide] Error: {exc}")
        exit(1)
