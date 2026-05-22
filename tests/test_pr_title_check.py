from __future__ import annotations

import pytest

from odev.git.pr_title_check.check_pr_title import (
    pr_title_hook,
    validate_pr_title,
)


def test_validate_pr_title_accepts_type_emoji_and_description() -> None:
    assert validate_pr_title("feat: 🎉 add PR title checker") == []


def test_validate_pr_title_accepts_scope_and_breaking_marker() -> None:
    assert validate_pr_title("ci(pr-title)!: 👷 require styled PR titles") == []


def test_validate_pr_title_rejects_empty_title() -> None:
    assert validate_pr_title("\n") == ["Pull request title is empty."]


def test_validate_pr_title_rejects_invalid_format() -> None:
    assert validate_pr_title("fix missing emoji") == [
        "Pull request title does not match the required format."
    ]


def test_validate_pr_title_rejects_unsupported_type() -> None:
    assert validate_pr_title("oops: 🔧 unsupported type") == [
        "Unsupported pull request title type: 'oops'."
    ]


def test_validate_pr_title_rejects_wrong_emoji() -> None:
    assert validate_pr_title("feat: 🐛 wrong emoji") == [
        "Wrong emoji for pull request title type 'feat': expected 🎉, got 🐛."
    ]


def test_pr_title_hook_reports_pr_title_context(tmp_path, capsys) -> None:
    pr_title_file = tmp_path / "pr_title.txt"
    pr_title_file.write_text("feat: 🐛 wrong emoji", encoding="utf-8")

    assert pr_title_hook([str(pr_title_file)]) == 1

    output = capsys.readouterr().out
    assert "[pr-title-check] Invalid pull request title:" in output
    assert "Wrong emoji for pull request title type 'feat'" in output
    assert "commit message" not in output.lower()
    assert "odev-commit-msg" not in output


def test_pr_title_hook_help_uses_pr_title_command(capsys) -> None:
    with pytest.raises(SystemExit) as exc_info:
        pr_title_hook(["--help"])

    assert exc_info.value.code == 0

    output = capsys.readouterr().out
    assert "usage: odev-pr-title-check" in output
    assert "pull request titles" in output
    assert "commit message" not in output.lower()
    assert "odev-commit-msg" not in output
