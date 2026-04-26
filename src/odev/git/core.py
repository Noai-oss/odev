from __future__ import annotations

import subprocess
from collections.abc import Sequence
from pathlib import Path
import shutil
import shlex

class GitError(RuntimeError):
    """Raised when a git command cannot be completed."""



def format_command(command: Sequence[str]) -> str:
    return shlex.join(command)

def git(
    args: Sequence[str],
    *,
    cwd: Path | str | None = None,
    check: bool = True,
    capture: bool = True,
) -> subprocess.CompletedProcess[str]:
    if shutil.which("git") is None:
        raise GitError("git executable was not found in PATH")

    command = ["git", *args]
    result = subprocess.run(
        command,
        cwd=cwd,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
        capture_output=capture,
    )

    if check and result.returncode != 0:
        message = (result.stderr or result.stdout or "").strip()
        if not message:
            message = f"`{format_command(command)}` failed with exit code {result.returncode}"
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
