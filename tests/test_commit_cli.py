from __future__ import annotations

from types import SimpleNamespace

import pytest

from odev.git.commit import cli


def test_save_last_commit_message_stores_full_message(tmp_path, monkeypatch) -> None:
    cache_path = tmp_path / "last-message"
    monkeypatch.setattr(cli, "last_commit_message_path", lambda: cache_path)

    cli.save_last_commit_message("fix(cli): 🐛 reuse last message\n\nbody")

    assert (
        cache_path.read_text(encoding="utf-8")
        == "fix(cli): 🐛 reuse last message\n\nbody\n"
    )
    assert cli.load_last_commit_message() == "fix(cli): 🐛 reuse last message\n\nbody"


def test_save_last_commit_message_ignores_empty_message(tmp_path, monkeypatch) -> None:
    cache_path = tmp_path / "last-message"
    monkeypatch.setattr(cli, "last_commit_message_path", lambda: cache_path)

    cli.save_last_commit_message(" \n\t ")

    assert not cache_path.exists()


def test_load_last_commit_message_returns_none_when_missing(
    tmp_path, monkeypatch
) -> None:
    monkeypatch.setattr(cli, "last_commit_message_path", lambda: tmp_path / "missing")

    assert cli.load_last_commit_message() is None


def test_run_commit_saves_successful_message(tmp_path, monkeypatch) -> None:
    commands: list[list[str]] = []
    cache_path = tmp_path / "last-message"

    def fake_run(command: list[str]):
        commands.append(command)
        return SimpleNamespace(returncode=0)

    monkeypatch.setattr(cli, "last_commit_message_path", lambda: cache_path)
    monkeypatch.setattr(cli.subprocess, "run", fake_run)

    assert cli.run_commit("feat: 🎉 add reuse command") == 0
    assert commands == [["git", "commit", "-F", str(cache_path)]]
    assert cache_path.read_text(encoding="utf-8") == "feat: 🎉 add reuse command\n"


def test_run_commit_can_signoff(tmp_path, monkeypatch) -> None:
    commands: list[list[str]] = []
    cache_path = tmp_path / "last-message"

    def fake_run(command: list[str]):
        commands.append(command)
        return SimpleNamespace(returncode=0)

    monkeypatch.setattr(cli, "last_commit_message_path", lambda: cache_path)
    monkeypatch.setattr(cli.subprocess, "run", fake_run)

    assert cli.run_commit("feat: 🎉 add signoff flag", signoff=True) == 0
    assert commands == [["git", "commit", "-s", "-F", str(cache_path)]]


def test_run_commit_saves_failed_attempt_message(tmp_path, monkeypatch) -> None:
    cache_path = tmp_path / "last-message"

    monkeypatch.setattr(cli, "last_commit_message_path", lambda: cache_path)
    monkeypatch.setattr(
        cli.subprocess,
        "run",
        lambda command: SimpleNamespace(returncode=1),
    )

    assert cli.run_commit("feat: 🎉 add reuse command") == 1
    assert cache_path.read_text(encoding="utf-8") == "feat: 🎉 add reuse command\n"


def test_run_commit_rejects_empty_message(monkeypatch, capsys) -> None:
    commands: list[list[str]] = []

    monkeypatch.setattr(cli.subprocess, "run", lambda command: commands.append(command))

    assert cli.run_commit(" \n\t ") == 1
    assert commands == []
    assert "Commit message is empty" in capsys.readouterr().err


def test_reuse_last_commit_message_runs_cached_message(monkeypatch) -> None:
    used_messages: list[tuple[str, bool]] = []
    confirm_defaults: list[bool | None] = []

    def fake_confirm(message: str, **kwargs):
        confirm_defaults.append(kwargs.get("default"))
        return SimpleNamespace(ask=lambda: True)

    monkeypatch.setattr(cli, "load_last_commit_message", lambda: "fix: 🐛 retry commit")
    monkeypatch.setattr(
        cli,
        "run_commit",
        lambda message, *, signoff: used_messages.append((message, signoff)) or 0,
    )
    monkeypatch.setattr(cli.questionary, "confirm", fake_confirm)

    assert cli.reuse_last_commit_message() == 0
    assert used_messages == [("fix: 🐛 retry commit", False)]
    assert confirm_defaults == [None]


def test_reuse_last_commit_message_can_be_aborted(monkeypatch) -> None:
    used_messages: list[tuple[str, bool]] = []
    confirm_defaults: list[bool | None] = []

    def fake_confirm(message: str, **kwargs):
        confirm_defaults.append(kwargs.get("default"))
        return SimpleNamespace(ask=lambda: False)

    monkeypatch.setattr(cli, "load_last_commit_message", lambda: "fix: 🐛 retry commit")
    monkeypatch.setattr(
        cli,
        "run_commit",
        lambda message, *, signoff: used_messages.append((message, signoff)) or 0,
    )
    monkeypatch.setattr(cli.questionary, "confirm", fake_confirm)

    assert cli.reuse_last_commit_message() == 0
    assert used_messages == []
    assert confirm_defaults == [None]


def test_reuse_last_commit_message_can_signoff(monkeypatch) -> None:
    used_messages: list[tuple[str, bool]] = []

    monkeypatch.setattr(cli, "load_last_commit_message", lambda: "fix: 🐛 retry commit")
    monkeypatch.setattr(
        cli.questionary, "confirm", lambda message: SimpleNamespace(ask=lambda: True)
    )
    monkeypatch.setattr(
        cli,
        "run_commit",
        lambda message, *, signoff: used_messages.append((message, signoff)) or 0,
    )

    assert cli.reuse_last_commit_message(signoff=True) == 0
    assert used_messages == [("fix: 🐛 retry commit", True)]


def test_reuse_last_commit_message_fails_without_cache(monkeypatch, capsys) -> None:
    monkeypatch.setattr(cli, "load_last_commit_message", lambda: None)

    assert cli.reuse_last_commit_message() == 1
    assert "No cached commit message found" in capsys.readouterr().err


def test_prompt_commit_message_requires_description(monkeypatch) -> None:
    validators = []

    monkeypatch.setattr(
        cli.questionary,
        "select",
        lambda message, choices: SimpleNamespace(ask=lambda: "fix"),
    )

    def fake_text(message: str, **kwargs):
        if "description" in message:
            validators.append(kwargs["validate"])
            return SimpleNamespace(ask=lambda: "retry commit")
        return SimpleNamespace(ask=lambda: "cli")

    monkeypatch.setattr(cli.questionary, "text", fake_text)

    assert cli.prompt_commit_message() == ("fix(cli): 🐛 retry commit", 0)
    assert validators[0]("") == "Description is required."
    assert validators[0]("retry\ncommit") == "Description must be a single line."
    assert validators[0]("retry commit") is True


def test_prompt_commit_message_can_omit_emoji(monkeypatch) -> None:
    monkeypatch.setattr(
        cli.questionary,
        "select",
        lambda message, choices: SimpleNamespace(ask=lambda: "fix"),
    )

    def fake_text(message: str, **kwargs):
        if "description" in message:
            return SimpleNamespace(ask=lambda: "retry commit")
        return SimpleNamespace(ask=lambda: "cli")

    monkeypatch.setattr(cli.questionary, "text", fake_text)

    assert cli.prompt_commit_message(include_emoji=False) == (
        "fix(cli): retry commit",
        0,
    )


def test_prompt_commit_message_treats_cancelled_description_as_cancel(
    monkeypatch,
) -> None:
    monkeypatch.setattr(
        cli.questionary,
        "select",
        lambda message, choices: SimpleNamespace(ask=lambda: "fix"),
    )

    def fake_text(message: str, **kwargs):
        if "description" in message:
            return SimpleNamespace(ask=lambda: None)
        return SimpleNamespace(ask=lambda: "cli")

    monkeypatch.setattr(cli.questionary, "text", fake_text)

    assert cli.prompt_commit_message() == (None, 0)


def test_prepare_index_aborts_when_staging_is_declined(monkeypatch, capsys) -> None:
    confirm_defaults: list[bool | None] = []

    def fake_confirm(message: str, **kwargs):
        confirm_defaults.append(kwargs.get("default"))
        return SimpleNamespace(ask=lambda: False)

    monkeypatch.setattr(cli, "check_unstaged_changes", lambda: True)
    monkeypatch.setattr(cli.questionary, "confirm", fake_confirm)

    assert cli.prepare_index() == 0
    assert "Commit aborted." in capsys.readouterr().out
    assert confirm_defaults == [None]


def test_prepare_index_continues_when_no_index_work_is_needed(monkeypatch) -> None:
    monkeypatch.setattr(cli, "check_unstaged_changes", lambda: False)

    assert cli.prepare_index() is None


def test_main_stops_when_prepare_index_aborts(monkeypatch) -> None:
    calls: list[str] = []

    monkeypatch.setattr(cli, "check_inside_git_repo", lambda: True)
    monkeypatch.setattr(cli, "prepare_index", lambda: 0)
    monkeypatch.setattr(cli, "reuse_last_commit_message", lambda: calls.append("reuse"))
    monkeypatch.setattr(cli, "interactive_commit", lambda: calls.append("interactive"))

    assert cli.main(["reuse"]) == 0
    assert calls == []


def test_main_routes_reuse_command(monkeypatch) -> None:
    calls: list[tuple[str, bool]] = []

    monkeypatch.setattr(cli, "check_inside_git_repo", lambda: True)
    monkeypatch.setattr(cli, "prepare_index", lambda: None)
    monkeypatch.setattr(
        cli,
        "reuse_last_commit_message",
        lambda *, signoff: calls.append(("reuse", signoff)) or 0,
    )
    monkeypatch.setattr(
        cli, "interactive_commit", lambda: calls.append("interactive") or 0
    )

    assert cli.main(["reuse"]) == 0
    assert calls == [("reuse", False)]


@pytest.mark.parametrize("argv", [["reuse", "-s"], ["-s", "reuse"]])
def test_main_routes_reuse_command_with_signoff(
    argv: list[str],
    monkeypatch,
) -> None:
    calls: list[tuple[str, bool]] = []

    monkeypatch.setattr(cli, "check_inside_git_repo", lambda: True)
    monkeypatch.setattr(cli, "prepare_index", lambda: None)
    monkeypatch.setattr(
        cli,
        "reuse_last_commit_message",
        lambda *, signoff: calls.append(("reuse", signoff)) or 0,
    )
    monkeypatch.setattr(
        cli, "interactive_commit", lambda: calls.append("interactive") or 0
    )

    assert cli.main(argv) == 0
    assert calls == [("reuse", True)]


@pytest.mark.parametrize("flag", ["--ignore-emoji", "-i"])
def test_main_passes_ignore_emoji_to_interactive_commit(
    flag: str,
    monkeypatch,
) -> None:
    calls: list[tuple[bool, bool]] = []

    monkeypatch.setattr(cli, "check_inside_git_repo", lambda: True)
    monkeypatch.setattr(cli, "prepare_index", lambda: None)
    monkeypatch.setattr(
        cli,
        "interactive_commit",
        lambda *, include_emoji, signoff: calls.append((include_emoji, signoff)) or 0,
    )

    assert cli.main([flag]) == 0
    assert calls == [(False, False)]


def test_main_passes_signoff_to_interactive_commit(monkeypatch) -> None:
    calls: list[tuple[bool, bool]] = []

    monkeypatch.setattr(cli, "check_inside_git_repo", lambda: True)
    monkeypatch.setattr(cli, "prepare_index", lambda: None)
    monkeypatch.setattr(
        cli,
        "interactive_commit",
        lambda *, include_emoji, signoff: calls.append((include_emoji, signoff)) or 0,
    )

    assert cli.main(["-s"]) == 0
    assert calls == [(True, True)]
