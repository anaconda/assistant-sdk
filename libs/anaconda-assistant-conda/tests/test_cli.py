import pytest
from typer.testing import CliRunner
from pytest import MonkeyPatch
from pytest_mock import MockerFixture

from anaconda_assistant_conda.cli import app
from anaconda_assistant_conda.config import AssistantCondaConfig


@pytest.mark.usefixtures("is_not_a_tty")
def test_assist_search_not_logged_in(
    mocked_assistant_domain: str, monkeypatch: MonkeyPatch
) -> None:
    monkeypatch.setenv("ANACONDA_ASSISTANT_ACCEPTED_TERMS", "true")
    monkeypatch.setenv("ANACONDA_ASSISTANT_DATA_COLLECTION", "true")
    monkeypatch.setenv("ANACONDA_ASSISTANT_DOMAIN", mocked_assistant_domain)
    monkeypatch.setenv("ANACONDA_AUTH_DOMAIN", mocked_assistant_domain)
    monkeypatch.delenv("ANACONDA_AUTH_API_KEY", raising=False)

    runner = CliRunner()
    result = runner.invoke(app, args=("search", "..."))
    assert result.exit_code == 0
    assert "AuthenticationMissingError: Login is required" in result.output
    assert "interactive login" not in result.output


@pytest.mark.usefixtures("is_a_tty")
def test_assist_search_not_logged_in_tty(
    mocked_assistant_domain: str, monkeypatch: MonkeyPatch, mocker: MockerFixture
) -> None:
    monkeypatch.setenv("ANACONDA_ASSISTANT_ACCEPTED_TERMS", "true")
    monkeypatch.setenv("ANACONDA_ASSISTANT_DATA_COLLECTION", "true")
    monkeypatch.setenv("ANACONDA_ASSISTANT_DOMAIN", mocked_assistant_domain)
    monkeypatch.setenv("ANACONDA_AUTH_DOMAIN", mocked_assistant_domain)
    monkeypatch.delenv("ANACONDA_AUTH_API_KEY", raising=False)

    login = mocker.patch("anaconda_auth.cli.login")

    runner = CliRunner()
    result = runner.invoke(app, args=("search", "..."), input="n")
    login.assert_not_called()

    assert result.exit_code == 0
    assert "AuthenticationMissingError: Login is required" in result.output
    assert "interactive login" in result.output

    result = runner.invoke(app, args=("search", "..."), input="y")
    login.assert_called_once()


def test_assist_search_system_message(
    mocked_assistant_domain: str, monkeypatch: MonkeyPatch, mocker: MockerFixture
) -> None:
    monkeypatch.setenv("ANACONDA_ASSISTANT_ACCEPTED_TERMS", "true")
    monkeypatch.setenv("ANACONDA_ASSISTANT_DATA_COLLECTION", "true")
    monkeypatch.setenv("ANACONDA_ASSISTANT_DOMAIN", mocked_assistant_domain)
    monkeypatch.setenv("ANACONDA_AUTH_DOMAIN", mocked_assistant_domain)
    monkeypatch.setenv("ANACONDA_AUTH_API_KEY", "api-key")

    import anaconda_assistant_conda.cli

    spy = mocker.spy(anaconda_assistant_conda.cli, "stream_response")

    runner = CliRunner()
    _ = runner.invoke(app, args=("search", "..."))

    config = AssistantCondaConfig()
    assert (
        spy.call_args.kwargs.get("system_message", "") == config.system_messages.search
    )
