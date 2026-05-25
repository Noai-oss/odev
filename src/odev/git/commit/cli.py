from __future__ import annotations

import argparse
import subprocess
import sys
from collections.abc import Sequence
from pathlib import Path

import questionary
from odev.git.conventional_subject import CONVENTIONAL_TYPES
from odev.git.core import check_inside_git_repo, git, git_path

LAST_COMMIT_MESSAGE_FILE = "odev-commit-last-message"


def last_commit_message_path() -> Path:
    return git_path(LAST_COMMIT_MESSAGE_FILE)


def save_last_commit_message(commit_msg: str) -> None:
    message = commit_msg.strip()
    if not message:
        return

    path = last_commit_message_path()
    path.write_text(f"{message}\n", encoding="utf-8")


def load_last_commit_message() -> str | None:
    path = last_commit_message_path()
    if not path.exists():
        return None

    message = path.read_text(encoding="utf-8").strip()
    return message if message else None


def check_unstaged_changes() -> bool:
    result = git(["status", "--porcelain"], check=False)
    if result.returncode != 0:
        return False

    for line in result.stdout.splitlines():
        if line.startswith("??") or len(line) > 1 and line[1] != " ":
            return True

    return False


def prepare_index() -> int | None:
    if check_unstaged_changes():
        need_stage = questionary.confirm(
            "You have unstaged changes. Do you want to stage them before committing?"
        ).ask()
        if need_stage is True:
            add_result = git(["add", "-A"], check=False)
            if add_result.returncode != 0:
                print("Error: Failed to stage changes.", file=sys.stderr)
                return 1
        else:
            print("Commit aborted.")
            return 0

    return None


def run_commit(commit_msg: str, *, signoff: bool = False) -> int:
    if not commit_msg.strip():
        print("Error: Commit message is empty.", file=sys.stderr)
        return 1

    save_last_commit_message(commit_msg)
    command = ["git", "commit"]
    if signoff:
        command.append("-s")
    command.extend(["-F", str(last_commit_message_path())])
    result = subprocess.run(command)
    return result.returncode


def require_description(value: str) -> bool | str:
    if not value.strip():
        return "Description is required."
    if "\n" in value or "\r" in value:
        return "Description must be a single line."
    return True


def confirm_commit() -> bool:
    confirm = questionary.confirm("Proceed with commit?").ask()
    return confirm is True


def prompt_commit_message(*, include_emoji: bool = True) -> tuple[str | None, int]:
    choices = [
        questionary.Choice(
            title=(
                f"{emoji} {name:<8} - {desc}"
                if include_emoji
                else f"{name:<8} - {desc}"
            ),
            value=name,
        )
        for name, (emoji, desc) in CONVENTIONAL_TYPES.items()
    ]

    commit_type = questionary.select(
        "Select the type of change you're committing:", choices=choices
    ).ask()

    if not commit_type:
        return None, 0

    scope = questionary.text(
        "What is the scope of this change? (Press enter to skip)"
    ).ask()
    if scope is None:
        return None, 0
    scope = scope.strip()

    desc = questionary.text(
        "Write a short, imperative tense description of the change:",
        validate=require_description,
    ).ask()
    if desc is None:
        return None, 0
    desc = desc.strip()
    if not desc:
        return None, 0

    scope_str = f"({scope})" if scope else ""
    if include_emoji:
        emoji = CONVENTIONAL_TYPES[commit_type][0]
        return f"{commit_type}{scope_str}: {emoji} {desc}", 0

    return f"{commit_type}{scope_str}: {desc}", 0


def interactive_commit(
    *,
    include_emoji: bool = True,
    signoff: bool = False,
) -> int:
    commit_msg, prompt_result = prompt_commit_message(include_emoji=include_emoji)
    if not commit_msg:
        return prompt_result

    print(f"\nProposed commit message:\n  {commit_msg}\n")

    if not confirm_commit():
        print("Commit aborted.")
        return 0

    return run_commit(commit_msg, signoff=signoff)


def reuse_last_commit_message(*, signoff: bool = False) -> int:
    commit_msg = load_last_commit_message()
    if not commit_msg:
        print(
            "Error: No cached commit message found. Run odev-commit once first.",
            file=sys.stderr,
        )
        return 1

    print(f"Reusing commit message:\n  {commit_msg}\n")
    if not confirm_commit():
        print("Commit aborted.")
        return 0

    return run_commit(commit_msg, signoff=signoff)


def main(argv: Sequence[str] | None = None) -> int:
    signoff_help = "Pass -s/--signoff to git commit."
    signoff_parser = argparse.ArgumentParser(add_help=False)
    signoff_parser.add_argument(
        "-s",
        "--signoff",
        action="store_true",
        default=argparse.SUPPRESS,
        help=signoff_help,
    )
    parser = argparse.ArgumentParser(
        prog="odev-commit",
        usage="%(prog)s [options] [reuse]",
        description="Create styled git commits with a guided prompt.",
        parents=[signoff_parser],
    )
    parser.add_argument(
        "-i",
        "--ignore-emoji",
        action="store_true",
        help="Create commit messages without an emoji.",
    )
    subparsers = parser.add_subparsers(dest="command")
    subparsers.add_parser(
        "reuse",
        prog="odev-commit reuse",
        parents=[signoff_parser],
        help="Commit with the last cached odev-commit message.",
    )
    args = parser.parse_args(argv)
    signoff = getattr(args, "signoff", False)

    if not check_inside_git_repo():
        print("Error: Not inside a git repository.", file=sys.stderr)
        return 1

    prepare_result = prepare_index()
    if prepare_result is not None:
        return prepare_result

    if args.command == "reuse":
        return reuse_last_commit_message(signoff=signoff)

    return interactive_commit(
        include_emoji=not args.ignore_emoji,
        signoff=signoff,
    )


if __name__ == "__main__":
    sys.exit(main())
