from __future__ import annotations

import pytest

from odev.git.commit_msg_check.check_commit_msg import validate_commit_msg, commit_msg_hook


def test_validate_accepts_type_emoji_and_description() -> None:
    assert validate_commit_msg("feat: 🎉 add commit message checker") == []


def test_validate_accepts_scope_and_breaking_marker() -> None:
    assert validate_commit_msg("fix(git/hook)!: 🐛 reject invalid messages") == []


def test_validate_uses_first_non_comment_line() -> None:
    commit_msg = """
    # Please enter the commit message for your changes.

    docs(readme): 📝 document commit convention

    Extra body text is ignored by the subject checker.
    """

    assert validate_commit_msg(commit_msg) == []


@pytest.mark.parametrize("prefix", ["Merge ", "Revert ", "fixup! ", "squash! "])
def test_validate_ignores_git_generated_subjects(prefix: str) -> None:
    assert validate_commit_msg(f"{prefix}whatever git generated") == []


def test_validate_rejects_empty_message() -> None:
    assert validate_commit_msg("\n# only comments\n") == ["Commit message is empty."]


def test_validate_rejects_invalid_format() -> None:
    assert validate_commit_msg("fix missing emoji") == [
        "Commit subject does not match the required format."
    ]


def test_validate_rejects_unsupported_type() -> None:
    assert validate_commit_msg("oops: 🔧 unsupported type") == [
        "Unsupported commit type: 'oops'."
    ]


def test_validate_rejects_wrong_emoji() -> None:
    assert validate_commit_msg("feat: 🐛 wrong emoji") == [
        "Wrong emoji for type 'feat': expected 🎉, got 🐛."
    ]


def test_commit_msg_hook_accepts_valid_commit_file(tmp_path) -> None:
    commit_msg_file = tmp_path / "COMMIT_EDITMSG"
    commit_msg_file.write_text("fix(cli): 🐛 handle missing exclude file", encoding="utf-8")

    assert commit_msg_hook([str(commit_msg_file)]) == 0


def test_commit_msg_hook_rejects_invalid_commit_file(tmp_path, capsys) -> None:
    commit_msg_file = tmp_path / "COMMIT_EDITMSG"
    commit_msg_file.write_text("feat: 🐛 wrong emoji", encoding="utf-8")

    assert commit_msg_hook([str(commit_msg_file)]) == 1

    assert "Wrong emoji for type 'feat'" in capsys.readouterr().out
