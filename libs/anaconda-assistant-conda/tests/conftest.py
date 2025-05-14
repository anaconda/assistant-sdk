import json
from functools import partial
from pathlib import Path
from typing import Any
from typing import Generator
from typing import IO
from typing import Mapping
from typing import Optional
from typing import Protocol
from typing import Sequence
from typing import Union
from typing import cast

import pytest
import requests
import responses
import typer
from typer.testing import CliRunner
from click.testing import Result
from pytest import MonkeyPatch
from pytest_mock import MockerFixture

from anaconda_cli_base.cli import app
from anaconda_assistant.api_client import APIClient


@pytest.fixture()
def tmp_cwd(monkeypatch: MonkeyPatch, tmp_path: Path) -> Path:
    """Create & return a temporary directory after setting current working directory to it."""
    monkeypatch.chdir(tmp_path)
    return tmp_path


@pytest.fixture(scope="session")
def is_not_none() -> Any:
    """
    An object that can be used to test whether another is None.

    This is particularly useful when testing contents of collections, e.g.:

    ```python
    def test_data(data, is_not_none):
        assert data == {"some_key": is_not_none, "some_other_key": 5}
    ```

    """

    class _NotNone:
        def __eq__(self, other: Any) -> bool:
            return other is not None

    return _NotNone()


class CLIInvoker(Protocol):
    def __call__(
        self,
        # app: typer.Typer,
        args: Optional[Union[str, Sequence[str]]] = None,
        input: Optional[Union[bytes, str, IO[Any]]] = None,
        env: Optional[Mapping[str, str]] = None,
        catch_exceptions: bool = True,
        color: bool = False,
        **extra: Any,
    ) -> Result: ...


@pytest.fixture()
def invoke_cli() -> CLIInvoker:
    """Returns a function, which can be used to call the CLI from within a temporary directory."""

    runner = CliRunner()

    return partial(runner.invoke, cast(typer.Typer, app))


@pytest.fixture
def is_a_tty(mocker: MockerFixture) -> Generator[None, None, None]:
    mocked1 = mocker.patch("anaconda_auth.cli.sys")
    mocked1.stdout.isatty.return_value = True

    mocked2 = mocker.patch("anaconda_assistant_conda.plugin.sys")
    mocked2.stdout.isatty.return_value = True

    mocked3 = mocker.patch("anaconda_assistant_conda.cli.sys")
    mocked3.stdout.isatty.return_value = True
    yield


@pytest.fixture
def is_not_a_tty(mocker: MockerFixture) -> Generator[None, None, None]:
    mocked1 = mocker.patch("anaconda_auth.cli.sys")
    mocked1.stdout.isatty.return_value = False

    mocked2 = mocker.patch("anaconda_assistant_conda.plugin.sys")
    mocked2.stdout.isatty.return_value = False

    mocked3 = mocker.patch("anaconda_assistant_conda.cli.sys")
    mocked3.stdout.isatty.return_value = False
    yield


@pytest.fixture
def mocked_assistant_domain(mocker: MockerFixture) -> Generator[str, None, None]:
    mocker.patch(
        "anaconda_auth.client.BaseClient.email",
        return_value="me@example.com",
        new_callable=mocker.PropertyMock,
    )

    api_client = APIClient(domain="mocking-assistant")

    with responses.RequestsMock() as resp:

        def api_key_required(request: requests.PreparedRequest) -> tuple:
            if "Authorization" not in request.headers:
                return (401, {}, json.dumps({"error": {"code": "auth_required"}}))
            elif request.headers["Authorization"] != "Bearer api-key":
                return (403, {}, "Incorrect access token")
            else:
                body = (
                    "I am Anaconda Assistant, an AI designed to help you with a variety of tasks, "
                    "answer questions, and provide information on a wide range of topics. How can "
                    "I assist you today?__TOKENS_42/424242__"
                )
                return (201, {}, body)

        resp.add_callback(
            responses.POST,
            api_client.urljoin("/completions"),
            callback=api_key_required,
        )
        yield api_client.config.domain


@pytest.fixture
def mock_anaconda_config_toml(
    tmp_path: Path, monkeypatch: MonkeyPatch
) -> Generator[None, None, None]:
    anaconda_config_toml = tmp_path / ".anaconda" / "config.toml"
    monkeypatch.setenv("ANACONDA_CONFIG_TOML", str(anaconda_config_toml))
    yield
