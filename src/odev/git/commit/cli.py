from __future__ import annotations

import subprocess
import sys

import questionary
from odev.git.commit_msg_check.check_commit_msg import COMMIT_TYPES


def main() -> int:
    choices = [
        questionary.Choice(title=f"{emoji} {name:<8} - {desc}", value=name)
        for name, (emoji, desc) in COMMIT_TYPES.items()
    ]

    commit_type = questionary.select(
        "Select the type of change you're committing:", choices=choices
    ).ask()

    if not commit_type:
        return 0

    scope = questionary.text(
        "What is the scope of this change? (Press enter to skip)"
    ).ask()
    if scope is None:
        return 0
    scope = scope.strip()

    desc = questionary.text(
        "Write a short, imperative tense description of the change:"
    ).ask()
    if not desc:
        print("Description goes cancelled or empty.", file=sys.stderr)
        return 1
    desc = desc.strip()

    emoji = COMMIT_TYPES[commit_type][0]
    scope_str = f"({scope})" if scope else ""
    commit_msg = f"{commit_type}{scope_str}: {emoji} {desc}"

    print(f"\nProposed commit message:\n  {commit_msg}\n")

    confirm = questionary.confirm("Proceed with commit?").ask()
    if not confirm:
        print("Commit aborted.")
        return 0

    result = subprocess.run(["git", "commit", "-m", commit_msg])
    return result.returncode


if __name__ == "__main__":
    sys.exit(main())
