from shutil import copy
from textwrap import dedent
from typing import cast
from typing import Any
from typing import Callable
from typing import Generator
from typing import Type
from typing import Optional
from unittest.mock import patch

import tomli
import tomli_w
from anaconda_cli_base.config import anaconda_config_path
from anaconda_cli_base.exceptions import register_error_handler
from anaconda_cli_base.exceptions import ERROR_HANDLERS
from anaconda_assistant import ChatSession
from anaconda_assistant.exceptions import (
    UnspecifiedAcceptedTermsError,
    UnspecifiedDataCollectionChoice,
)
from rich.console import Console, Group
from rich.live import Live
from rich.prompt import Confirm
from .rich_customizations.md import MyMarkdown


def set_config(table: str, key: str, value: Any) -> None:
    expanded = table.split(".")

    # save a backup of the config.toml just to be safe
    config_toml = anaconda_config_path()
    if config_toml.exists():
        copy(config_toml, config_toml.with_suffix(".backup.toml"))
        with open(config_toml, "rb") as f:
            config = tomli.load(f)
    else:
        config = {}

    # Add table if it doesn't exist
    config_table = config
    for table_key in expanded:
        if table_key not in config_table:
            config_table[table_key] = {}
        config_table = config_table[table_key]

    # config_table is still referenced in the config dict
    # we can edit the value here and then write the whole dict back
    config_table[key] = value

    config_toml.parent.mkdir(parents=True, exist_ok=True)
    with open(config_toml, "wb") as f:
        tomli_w.dump(config, f)


@register_error_handler(UnspecifiedDataCollectionChoice)
def data_collection_choice(e: Type[UnspecifiedDataCollectionChoice]) -> int:
    import anaconda_auth.cli

    if not anaconda_auth.cli.sys.stdout.isatty():  # type: ignore
        print(e.args[0])
        return 1

    msg = dedent(
        """\
        You have not chosen to opt-in or opt-out of data collection.
        This does not affect the operation of Anaconda Assistant, but your choice is required to proceed.

        If you opt-in you will enjoy personalized recommendations and contribute to smarter features.
        We prioritize your privacy:

          * Your data is never sold
          * Always secured
          * This setting only affects the data Anaconda stores
          * It does not affect the data that is sent to Open AI

        [bold green]Would you like to opt-in to data collection?[/bold green]
        """
    )
    data_collection = Confirm.ask(msg)
    set_config("plugin.assistant", "data_collection", data_collection)

    return -1


@register_error_handler(UnspecifiedAcceptedTermsError)
def accept_terms(e: Type[UnspecifiedAcceptedTermsError]) -> int:
    import anaconda_auth.cli

    if not anaconda_auth.cli.sys.stdout.isatty():  # type: ignore
        print(e.args[0])
        return 1

    msg = dedent(
        """\
        You have not accepted the terms of service.
        You must accept our terms of service and Privacy Policy here

          https://anaconda.com/legal

        [bold green]Are you more than 13 years old and accept the terms?[/bold green]
        """
    )
    accepted_terms = Confirm.ask(msg)
    set_config("plugin.assistant", "accepted_terms", accepted_terms)

    if not accepted_terms:
        return 1
    else:
        return -1


def try_except_repeat(
    func: Callable, max_depth: int = 5, *args: Any, **kwargs: Any
) -> Any:
    if max_depth == 0:
        raise RuntimeError("try/except recursion exceeded")
    try:
        yield from func(*args, **kwargs)
    except Exception as e:
        callback = ERROR_HANDLERS[type(e)]
        exit_code = callback(e)
        if exit_code == -1:
            yield from try_except_repeat(
                func=func,
                max_depth=max_depth - 1,
                *args,
                **kwargs,  # type: ignore
            )
        else:
            return


def stream_response(
    system_message: str,
    prompt: str,
    is_a_tty: bool = True,
    console: Optional[Console] = None,
) -> None:
    if console is None:
        console = Console()

    full_text = ""
    with Live(
        MyMarkdown(full_text),
        vertical_overflow="visible",
        console=console,
        auto_refresh=False,
    ) as live:
        with patch("anaconda_auth.cli.sys") as mocked:
            mocked.stdout.isatty.return_value = is_a_tty

            def chat() -> Generator[str, None, None]:
                session = ChatSession(system_message=system_message)
                response = session.chat(message=prompt, stream=True)
                yield from response

            response = cast(
                Generator[str, None, None], try_except_repeat(chat, max_depth=5)
            )

            for chunk in response:
                full_text += chunk
                try:
                    md = MyMarkdown(full_text, hyperlinks=False)
                except Exception:
                    continue
                live.update(md, refresh=True)
