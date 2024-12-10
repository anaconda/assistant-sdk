from functools import partial
from pathlib import Path
from typing import Any
from typing import IO
from typing import Mapping
from typing import Optional
from typing import Protocol
from typing import Sequence
from typing import Union
from typing import cast

import pytest
import typer
from typer.testing import CliRunner
from click.testing import Result
from pytest import MonkeyPatch

from anaconda_cli_base.cli import app


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
@pytest.mark.usefixtures("tmp_cwd")
def invoke_cli() -> CLIInvoker:
    """Returns a function, which can be used to call the CLI from within a temporary directory."""

    runner = CliRunner()

    return partial(runner.invoke, cast(typer.Typer, app))
