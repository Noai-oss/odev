
from __future__ import annotations

import re
import sys
from io import TextIOWrapper
from pathlib import Path


COMMIT_TYPES: dict[str, tuple[str, str]] = {
    "feat": ("🎉", "A new feature"),
    "fix": ("🐛", "A bug fix"),
    "docs": ("📝", "Documentation only changes"),
    "style": ("🎨", "Code style changes"),
    "refactor": ("♻️", "Code changes that neither fix a bug nor add a feature"),
    "perf": ("⚡", "Performance improvements"),
    "test": ("✅", "Adding or updating tests"),
    "build": ("📦", "Build system or dependency changes"),
    "ci": ("👷", "CI configuration changes"),
    "chore": ("🔧", "Other maintenance changes"),
    "revert": ("⏪", "Revert a previous commit"),
}

COMMIT_RE = re.compile(
    r"^(?P<type>[a-z]+)(?:\((?P<scope>[a-z0-9._/-]+)\))?(?P<breaking>!)?: "
    r"(?P<emoji>\S+) (?P<description>.+)$"
)

IGNORED_PREFIXES = ("Merge ", "Revert ", "fixup! ", "squash! ")


def _configure_output() -> None:
    for stream in (sys.stdout, sys.stderr):
        if isinstance(stream, TextIOWrapper):
            stream.reconfigure(encoding="utf-8", errors="replace")


def _subject_line(commit_msg: str) -> str:
    for line in commit_msg.splitlines():
        subject = line.strip()
        if subject and not subject.startswith("#"):
            return subject
    return ""


def _format_rules() -> str:
    types = "\n".join(
        f"  {name:<8} {emoji}  {description}"
        for name, (emoji, description) in COMMIT_TYPES.items()
    )
    return (
        "Expected format:\n"
        "  <type>(<scope>): <emoji> <description>\n"
        "  <type>: <emoji> <description>\n\n"
        "Examples:\n"
        "  feat: 🎉 initial commit with git workflow helpers\n"
        "  fix(cli): 🐛 handle missing exclude file\n\n"
        "Allowed types:\n"
        f"{types}"
    )


def validate_commit_msg(commit_msg: str) -> list[str]:
    subject = _subject_line(commit_msg)
    if not subject:
        return ["Commit message is empty."]

    if subject.startswith(IGNORED_PREFIXES):
        return []

    match = COMMIT_RE.match(subject)
    if not match:
        return ["Commit subject does not match the required format."]

    commit_type = match.group("type")
    if commit_type not in COMMIT_TYPES:
        return [f"Unsupported commit type: {commit_type!r}."]

    expected_emoji = COMMIT_TYPES[commit_type][0]
    actual_emoji = match.group("emoji")
    if actual_emoji != expected_emoji:
        return [
            f"Wrong emoji for type {commit_type!r}: expected {expected_emoji}, "
            f"got {actual_emoji}."
        ]

    if not match.group("description").strip():
        return ["Commit description is empty."]

    return []


def main(commit_msg_file: str | Path | None = None) -> None:
    _configure_output()

    if commit_msg_file is None:
        if len(sys.argv) != 2:
            print("Only one argument expected: the path to the commit message file.")
            raise SystemExit(2)
        commit_msg_file = sys.argv[1]

    commit_msg_file = Path(commit_msg_file)
    commit_msg = commit_msg_file.read_text(encoding="utf-8")
    errors = validate_commit_msg(commit_msg)
    if errors:
        print("[commit-msg] Invalid commit message:")
        for error in errors:
            print(f"  - {error}")
        print()
        print(_format_rules())
        raise SystemExit(1)
