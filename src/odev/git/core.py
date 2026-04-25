from __future__ import annotations

import subprocess
from collections.abc import Sequence
from pathlib import Path


class GitError(RuntimeError):
    """Raised when a git command cannot be completed."""


def git(
    args: Sequence[str],
    *,
    cwd: Path | str | None = None,
    check: bool = True,
    capture: bool = True,
) -> subprocess.CompletedProcess[str]:
    command = ["git", *args]
    try:
        result = subprocess.run(
            command,
            cwd=cwd,
            text=True,
            check=False,
            capture_output=capture,
        )
    except FileNotFoundError as exc:
        raise GitError("git executable was not found in PATH") from exc

    if check and result.returncode != 0:
        message = ""
        if result.stderr:
            message = result.stderr.strip()
        elif result.stdout:
            message = result.stdout.strip()
        if not message:
            message = f"`{' '.join(command)}` failed with exit code {result.returncode}"
        raise GitError(message)

    return result


def ensure_repo() -> None:
    result = git(["rev-parse", "--is-inside-work-tree"], check=False)
    if result.returncode != 0 or result.stdout.strip() != "true":
        raise GitError("not inside a git work tree")


def git_path(path: str) -> Path:
    ensure_repo()
    result = git(
        [
            "rev-parse",
            "--path-format",
            "absolute",
            "--git-path",
            path,
        ]
    )
    return Path(result.stdout.strip()).resolve()


# def current_branch_name() -> str:
#     ensure_repo()
#     result = git(["branch", "--show-current", "--no-color"])
#     branch = result.stdout.strip()
#     if branch:
#         return branch

#     raise GitError("current HEAD is detached; no branch name is available")


# def default_branch(remote: str = "origin") -> str:
#     ensure_repo()
#     remote_info = git(["remote", "show", remote])
#     match = re.search(r"HEAD branch:\s*(.+)", remote_info.stdout)
#     if not match:
#         raise GitError(f"could not find default branch for remote `{remote}`")
#     return match.group(1).strip()
