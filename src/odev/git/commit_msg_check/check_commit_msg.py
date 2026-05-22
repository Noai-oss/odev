from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence
from io import TextIOWrapper
from pathlib import Path

from ..conventional_subject import (
    format_rules,
    validate_conventional_subject,
)

IGNORED_PREFIXES = ("Merge ", "Revert ", "fixup! ", "squash! ")

COMMIT_MSG_EXAMPLES = (
    "feat: 🎉 initial commit with git workflow helpers",
    "fix(cli): 🐛 handle missing exclude file",
)


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


def validate_commit_msg(commit_msg: str) -> list[str]:
    subject = _subject_line(commit_msg)
    return validate_conventional_subject(
        subject,
        empty_error="Commit message is empty.",
        invalid_format_error="Commit subject does not match the required format.",
        unsupported_type_error="Unsupported commit type: {conventional_type!r}.",
        wrong_emoji_error="Wrong emoji for type {conventional_type!r}: expected {expected_emoji}, got {actual_emoji}.",
        empty_description_error="Commit description is empty.",
        ignored_prefixes=IGNORED_PREFIXES,
    )


def commit_msg_hook(argv: Sequence[str] | None = None) -> int:
    _configure_output()
    parser = argparse.ArgumentParser(
        prog="odev-commit-msg",
        description="Validate commit messages with conventional format and emojis.",
    )
    parser.add_argument(
        "commit_msg_file",
        help="Path to the commit message file provided by git/pre-commit.",
    )
    args = parser.parse_args(argv)

    message_text = Path(args.commit_msg_file).read_text(encoding="utf-8")
    errors = validate_commit_msg(message_text)
    if errors:
        print("[commit-msg] Invalid commit message:")
        for error in errors:
            print(f"  - {error}")
        print()
        print(format_rules(COMMIT_MSG_EXAMPLES))
        return 1
    return 0
