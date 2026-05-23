from __future__ import annotations

import subprocess

from odev.git import core


def test_git_path_uses_path_format_equals_syntax(monkeypatch, tmp_path) -> None:
    commands: list[list[str]] = []
    expected_path = tmp_path / ".git" / "odev-commit-last-message"

    def mock_git(args: list[str], **_kwargs) -> subprocess.CompletedProcess[str]:
        commands.append(args)
        return subprocess.CompletedProcess(args, 0, f"{expected_path}\n", "")

    monkeypatch.setattr(core, "ensure_repo", lambda: None)
    monkeypatch.setattr(core, "git", mock_git)

    assert core.git_path("odev-commit-last-message") == expected_path.resolve()
    assert commands == [
        [
            "rev-parse",
            "--path-format=absolute",
            "--git-path",
            "odev-commit-last-message",
        ]
    ]
