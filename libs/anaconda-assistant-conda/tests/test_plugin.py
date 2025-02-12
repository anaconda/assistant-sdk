import pytest

from pytest import MonkeyPatch
from pytest_mock import MockerFixture
from anaconda_assistant_conda.plugin import error_handler
from anaconda_assistant_conda.plugin import AssistantCondaConfig
from conda.exception_handler import ExceptionHandler
from conda import CondaError
from conda.exceptions import PackagesNotFoundError


@pytest.mark.usefixtures("is_not_a_tty")
def test_error_handler_not_logged_in(
    mocked_assistant_domain: str,
    monkeypatch: MonkeyPatch,
    mocker: MockerFixture,
    capsys: pytest.CaptureFixture[str],
) -> None:
    monkeypatch.setenv("ANACONDA_ASSISTANT_ACCEPTED_TERMS", "true")
    monkeypatch.setenv("ANACONDA_ASSISTANT_DATA_COLLECTION", "true")
    monkeypatch.setenv("ANACONDA_ASSISTANT_DOMAIN", mocked_assistant_domain)
    monkeypatch.setenv("ANACONDA_CLOUD_DOMAIN", mocked_assistant_domain)
    monkeypatch.delenv("ANACONDA_CLOUD_API_KEY", raising=False)

    def mocked_command() -> None:
        raise CondaError("mocked-command failed")

    exception_handler = ExceptionHandler()
    mocker.patch("conda.exception_handler.sys.argv", ["conda", "command", "will-fail"])
    error_handler("mocked_command")
    exception_handler(mocked_command)

    assert "AuthenticationMissingError: Login is required" in capsys.readouterr().out


@pytest.mark.usefixtures("is_a_tty")
def test_error_handler_not_logged_in_tty_do_login(
    mocked_assistant_domain: str,
    monkeypatch: MonkeyPatch,
    mocker: MockerFixture,
    capsys: pytest.CaptureFixture[str],
) -> None:
    monkeypatch.setenv("ANACONDA_ASSISTANT_ACCEPTED_TERMS", "true")
    monkeypatch.setenv("ANACONDA_ASSISTANT_DATA_COLLECTION", "true")
    monkeypatch.setenv("ANACONDA_ASSISTANT_DOMAIN", mocked_assistant_domain)
    monkeypatch.setenv("ANACONDA_CLOUD_DOMAIN", mocked_assistant_domain)
    monkeypatch.delenv("ANACONDA_CLOUD_API_KEY", raising=False)

    def set_api_key() -> None:
        monkeypatch.setenv("ANACONDA_CLOUD_API_KEY", "api-key")

    login = mocker.patch("anaconda_cloud_auth.cli.login", side_effect=set_api_key)

    mocker.patch("rich.prompt.Confirm.ask", return_value=True)

    def mocked_command() -> None:
        raise CondaError("mocked-command failed")

    exception_handler = ExceptionHandler()
    mocker.patch("conda.exception_handler.sys.argv", ["conda", "command", "will-fail"])
    error_handler("mocked_command")
    exception_handler(mocked_command)

    stdout = capsys.readouterr().out
    assert "AuthenticationMissingError: Login is required" in stdout
    assert "I am Anaconda Assistant" in stdout
    login.assert_called_once()


@pytest.mark.usefixtures("is_a_tty")
def test_error_handler_not_logged_in_tty_do_not_login(
    mocked_assistant_domain: str,
    monkeypatch: MonkeyPatch,
    mocker: MockerFixture,
    capsys: pytest.CaptureFixture[str],
) -> None:
    monkeypatch.setenv("ANACONDA_ASSISTANT_ACCEPTED_TERMS", "true")
    monkeypatch.setenv("ANACONDA_ASSISTANT_DATA_COLLECTION", "true")
    monkeypatch.setenv("ANACONDA_ASSISTANT_DOMAIN", mocked_assistant_domain)
    monkeypatch.setenv("ANACONDA_CLOUD_DOMAIN", mocked_assistant_domain)
    monkeypatch.delenv("ANACONDA_CLOUD_API_KEY", raising=False)

    def set_api_key() -> None:
        monkeypatch.setenv("ANACONDA_CLOUD_API_KEY", "api-key")

    login = mocker.patch("anaconda_cloud_auth.cli.login", side_effect=set_api_key)

    mocker.patch("rich.prompt.Confirm.ask", return_value=False)

    def mocked_command() -> None:
        raise CondaError("mocked-command failed")

    exception_handler = ExceptionHandler()
    mocker.patch("conda.exception_handler.sys.argv", ["conda", "command", "will-fail"])
    error_handler("mocked_command")
    exception_handler(mocked_command)

    stdout = capsys.readouterr().out
    assert "AuthenticationMissingError: Login is required" in stdout
    assert "ANACONDA_CLOUD_API_KEY env var" in stdout
    login.assert_not_called()


def test_error_handler_send_error(
    mocked_assistant_domain: str, monkeypatch: MonkeyPatch, mocker: MockerFixture
) -> None:
    monkeypatch.setenv("ANACONDA_ASSISTANT_ACCEPTED_TERMS", "true")
    monkeypatch.setenv("ANACONDA_ASSISTANT_DATA_COLLECTION", "true")
    monkeypatch.setenv("ANACONDA_ASSISTANT_DOMAIN", mocked_assistant_domain)
    monkeypatch.setenv("ANACONDA_CLOUD_DOMAIN", mocked_assistant_domain)
    monkeypatch.setenv("ANACONDA_CLOUD_API_KEY", "api-key")

    import langchain_core.language_models

    chat = mocker.spy(langchain_core.language_models.BaseChatModel, "stream")

    def mocked_command() -> None:
        raise CondaError("mocked-command failed")

    exc = ExceptionHandler()
    mocker.patch("conda.exception_handler.sys.argv", ["conda", "command", "will-fail"])
    error_handler("mocked_command")
    exc(mocked_command)

    config = AssistantCondaConfig()
    messages = [
        {"role": "system", "content": config.system_messages.error},
        {
            "role": "user",
            "content": "COMMAND:\nconda command will-fail\nMESSAGE:\nCondaError: mocked-command failed",
        },
    ]
    assert chat.call_args.kwargs.get("input", []) == messages


def test_error_handler_search_condaerror(
    mocked_assistant_domain: str,
    monkeypatch: MonkeyPatch,
    mocker: MockerFixture,
) -> None:
    monkeypatch.setenv("ANACONDA_ASSISTANT_ACCEPTED_TERMS", "true")
    monkeypatch.setenv("ANACONDA_ASSISTANT_DATA_COLLECTION", "true")
    monkeypatch.setenv("ANACONDA_ASSISTANT_DOMAIN", mocked_assistant_domain)
    monkeypatch.setenv("ANACONDA_CLOUD_DOMAIN", mocked_assistant_domain)
    monkeypatch.setenv("ANACONDA_CLOUD_API_KEY", "api-key")

    import langchain_core.language_models

    chat = mocker.spy(langchain_core.language_models.BaseChatModel, "stream")

    def mocked_search() -> None:
        raise CondaError("search failed")

    exc = ExceptionHandler()
    mocker.patch("conda.exception_handler.sys.argv", ["conda", "search", "will-fail"])
    error_handler("search")
    exc(mocked_search)

    config = AssistantCondaConfig()
    messages = [
        {"role": "system", "content": config.system_messages.error},
        {
            "role": "user",
            "content": "COMMAND:\nconda search will-fail\nMESSAGE:\nCondaError: search failed",
        },
    ]

    assert chat.call_args.kwargs.get("input", []) == messages


def test_error_handler_search_packgenotfounderror(
    mocked_assistant_domain: str,
    monkeypatch: MonkeyPatch,
    mocker: MockerFixture,
    capsys: pytest.CaptureFixture[str],
) -> None:
    monkeypatch.setenv("ANACONDA_ASSISTANT_ACCEPTED_TERMS", "true")
    monkeypatch.setenv("ANACONDA_ASSISTANT_DATA_COLLECTION", "true")
    monkeypatch.setenv("ANACONDA_ASSISTANT_DOMAIN", mocked_assistant_domain)
    monkeypatch.setenv("ANACONDA_CLOUD_DOMAIN", mocked_assistant_domain)
    monkeypatch.setenv("ANACONDA_CLOUD_API_KEY", "api-key")

    import langchain_core.language_models

    chat = mocker.spy(langchain_core.language_models.BaseChatModel, "stream")

    def mocked_search() -> None:
        raise PackagesNotFoundError(packages=["will-fail"])

    exc = ExceptionHandler()
    mocker.patch("conda.exception_handler.sys.argv", ["conda", "search", "will-fail"])
    error_handler("search")
    exc(mocked_search)

    chat.assert_not_called()

    stderr = capsys.readouterr().err
    assert "conda assist search" in stderr
