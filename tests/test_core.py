from __future__ import annotations

import importlib
import importlib.metadata
import subprocess
from importlib.metadata import PackageNotFoundError

import odev
from odev.git import core


def test_package_version_comes_from_metadata() -> None:
    assert odev.__version__ == importlib.metadata.version("odev")


def test_package_version_falls_back_when_metadata_is_unavailable(monkeypatch) -> None:
    def raise_package_not_found(_name: str) -> str:
        raise PackageNotFoundError("odev")

    monkeypatch.setattr(importlib.metadata, "version", raise_package_not_found)
    reloaded = importlib.reload(odev)

    assert reloaded.__version__ == "0.0.0"

    monkeypatch.undo()
    importlib.reload(odev)


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
