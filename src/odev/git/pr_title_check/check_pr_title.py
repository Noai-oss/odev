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

PR_TITLE_EXAMPLES = (
    "feat: 🎉 add PR title checker",
    "ci(pr): 👷 validate pull request titles",
)

PR_TITLE_NO_EMOJI_EXAMPLES = (
    "feat: add PR title checker",
    "ci(pr): validate pull request titles",
)


def _configure_output() -> None:
    for stream in (sys.stdout, sys.stderr):
        if isinstance(stream, TextIOWrapper):
            stream.reconfigure(encoding="utf-8", errors="replace")


def validate_pr_title(
    pr_title: str,
    *,
    require_emoji: bool = True,
) -> list[str]:
    return validate_conventional_subject(
        pr_title.strip(),
        empty_error="Pull request title is empty.",
        invalid_format_error="Pull request title does not match the required format.",
        unsupported_type_error=(
            "Unsupported pull request title type: {conventional_type!r}."
        ),
        wrong_emoji_error=(
            "Wrong emoji for pull request title type {conventional_type!r}: "
            "expected {expected_emoji}, got {actual_emoji}."
        ),
        empty_description_error="Pull request title description is empty.",
        require_emoji=require_emoji,
    )


def pr_title_hook(argv: Sequence[str] | None = None) -> int:
    _configure_output()
    parser = argparse.ArgumentParser(
        prog="odev-pr-title-check",
        description=(
            "Validate pull request titles with conventional format and emojis."
        ),
    )
    parser.add_argument(
        "-i",
        "--ignore-emoji",
        action="store_true",
        help="Allow pull request titles without an emoji and skip emoji validation.",
    )
    parser.add_argument(
        "pr_title_file",
        help="Path to a file containing the pull request title.",
    )
    args = parser.parse_args(argv)

    title_text = Path(args.pr_title_file).read_text(encoding="utf-8")
    require_emoji = not args.ignore_emoji
    errors = validate_pr_title(title_text, require_emoji=require_emoji)
    if errors:
        print("[pr-title-check] Invalid pull request title:")
        for error in errors:
            print(f"  - {error}")
        print()
        examples = PR_TITLE_EXAMPLES if require_emoji else PR_TITLE_NO_EMOJI_EXAMPLES
        print(format_rules(examples, require_emoji=require_emoji))
        return 1
    return 0
