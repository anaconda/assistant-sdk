from shutil import copy
from textwrap import dedent
from typing import cast
from typing import Any
from typing import Callable
from typing import Generator
from typing import Type
from typing import Optional
from unittest.mock import patch

import tomlkit
from anaconda_cli_base.config import anaconda_config_path
from anaconda_cli_base.exceptions import register_error_handler
from anaconda_cli_base.exceptions import ERROR_HANDLERS
from anaconda_assistant.exceptions import (
    UnspecifiedAcceptedTermsError,
    UnspecifiedDataCollectionChoice,
)
from rich.console import Console
from rich.live import Live
from rich.markdown import Markdown
from rich.prompt import Confirm

from anaconda_assistant_conda.config import LLM


def set_config(table: str, key: str, value: Any) -> None:
    expanded = table.split(".")

    # save a backup of the config.toml just to be safe
    config_toml = anaconda_config_path()
    if config_toml.exists():
        copy(config_toml, config_toml.with_suffix(".backup.toml"))
        with open(config_toml, "rb") as f:
            config = tomlkit.load(f)
    else:
        config = tomlkit.document()

    # Add table if it doesn't exist
    config_table = config
    for table_key in expanded:
        if table_key not in config_table:  # type: ignore
            config_table[table_key] = tomlkit.table()  # type: ignore
        config_table = config_table[table_key]  # type: ignore

    # config_table is still referenced in the config doc
    # we can edit the value here and then write the whole doc back
    config_table[key] = value  # type: ignore

    config_toml.parent.mkdir(parents=True, exist_ok=True)
    with open(config_toml, "w") as f:
        tomlkit.dump(config, f)


@register_error_handler(UnspecifiedDataCollectionChoice)
def data_collection_choice(e: Type[UnspecifiedDataCollectionChoice]) -> int:
    import anaconda_cloud_auth.cli

    if not anaconda_cloud_auth.cli.sys.stdout.isatty():  # type: ignore
        print(e.args[0])
        return 1

    msg = dedent("""\
        You have not chosen to opt-in or opt-out of data collection.
        This does not affect the operation of Anaconda Assistant, but your choice is required to proceed.

        If you opt-in you will enjoy personalized recommendations and contribute to smarter features.
        We prioritize your privacy:

          * Your data is never sold
          * Always secured
          * This setting only affects the data Anaconda stores
          * It does not affect the data that is sent to Open AI

        [bold green]Would you like to opt-in to data collection?[/bold green]
        """)
    data_collection = Confirm.ask(msg)
    set_config("plugin.assistant", "data_collection", data_collection)

    return -1


@register_error_handler(UnspecifiedAcceptedTermsError)
def accept_terms(e: Type[UnspecifiedAcceptedTermsError]) -> int:
    import anaconda_cloud_auth.cli

    if not anaconda_cloud_auth.cli.sys.stdout.isatty():  # type: ignore
        print(e.args[0])
        return 1

    msg = dedent("""\
        You have not accepted the terms of service.
        You must accept our terms of service

          https://legal.anaconda.com/policies/en/?name=terms-of-service#anaconda-terms-of-service

        and Privacy Policy

          https://legal.anaconda.com/policies/en/?name=privacy-policy

        [bold green]Are you more than 13 years old and accept the terms?[/bold green]
        """)
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
    llm: LLM,
    system_message: str,
    prompt: str,
    is_a_tty: bool = True,
    console: Optional[Console] = None,
) -> None:
    if console is None:
        console = Console()

    full_text = ""
    with Live(
        Markdown(full_text),
        auto_refresh=False,
        vertical_overflow="visible",
        console=console,
    ) as live:
        with patch("anaconda_cloud_auth.cli.sys") as mocked:
            mocked.stdout.isatty.return_value = is_a_tty

            def chat() -> Generator[str, None, None]:
                if not llm.is_default_llm:
                    console.print(
                        "[red]Warning:[/red] Loading a custom LLM is an experimental feature. Use with caution."
                    )

                model = llm.load()

                if llm.combine_messages:
                    # Some models do not correctly respect a system message
                    # and we must provide a single message with all instructions.
                    messages = [
                        {"role": "user", "content": f"{system_message}\n{prompt}"},
                    ]
                else:
                    messages = [
                        {"role": "system", "content": system_message},
                        {"role": "user", "content": prompt},
                    ]
                response = model.stream(input=messages)
                for chunk in response:
                    yield cast(str, chunk.content)

            response = cast(
                Generator[str, None, None], try_except_repeat(chat, max_depth=5)
            )

            for chunk in response:
                full_text += chunk
                try:
                    md = Markdown(full_text, hyperlinks=False)
                except Exception:
                    continue
                live.update(md, refresh=True)
