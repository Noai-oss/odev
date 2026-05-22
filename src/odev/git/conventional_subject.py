from __future__ import annotations

import re
from collections.abc import Sequence

CONVENTIONAL_TYPES: dict[str, tuple[str, str]] = {
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

_ALLOWED_TYPES_STR = "\n".join(
    f"  {name:<8} {emoji}  {description}"
    for name, (emoji, description) in CONVENTIONAL_TYPES.items()
)

CONVENTIONAL_RE = re.compile(
    r"^(?P<type>[a-z]+)(?:\((?P<scope>[a-z0-9._/-]+)\))?(?P<breaking>!)?: "
    r"(?P<emoji>\S+) (?P<description>.+)$"
)

DEFAULT_EXAMPLES = (
    "feat: 🎉 add git workflow helpers",
    "fix(cli): 🐛 handle missing exclude file",
)


def format_rules(examples: Sequence[str] = DEFAULT_EXAMPLES) -> str:
    formatted_examples = "\n".join(f"  {example}" for example in examples)
    return (
        "Expected format:\n"
        "  <type>(<scope>): <emoji> <description>\n"
        "  <type>(<scope>)!: <emoji> <description> (breaking change)\n"
        "  <type>: <emoji> <description>\n"
        "  <type>!: <emoji> <description> (breaking change)\n\n"
        "Examples:\n"
        f"{formatted_examples}\n\n"
        "Allowed types:\n"
        f"{_ALLOWED_TYPES_STR}"
    )


def validate_conventional_subject(
    subject: str,
    *,
    empty_error: str,
    invalid_format_error: str,
    unsupported_type_error: str,
    wrong_emoji_error: str,
    empty_description_error: str,
    ignored_prefixes: Sequence[str] = (),
) -> list[str]:
    if not subject:
        return [empty_error]

    if subject.startswith(tuple(ignored_prefixes)):
        return []

    match = CONVENTIONAL_RE.match(subject)
    if not match:
        return [invalid_format_error]

    conventional_type = match.group("type")
    if conventional_type not in CONVENTIONAL_TYPES:
        return [unsupported_type_error.format(conventional_type=conventional_type)]

    expected_emoji = CONVENTIONAL_TYPES[conventional_type][0]
    actual_emoji = match.group("emoji")
    if actual_emoji != expected_emoji:
        return [
            wrong_emoji_error.format(
                conventional_type=conventional_type,
                expected_emoji=expected_emoji,
                actual_emoji=actual_emoji,
            )
        ]

    if not match.group("description").strip():
        return [empty_description_error]

    return []
