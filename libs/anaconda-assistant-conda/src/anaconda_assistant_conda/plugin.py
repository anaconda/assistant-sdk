import argparse
from typing import Generator, cast

from requests.exceptions import HTTPError

from anaconda_cli_base.console import console
from anaconda_cloud_auth.actions import login
from conda import plugins
from rich.markdown import Markdown
from rich.prompt import Confirm
from rich.live import Live

from anaconda_assistant import ChatSession
from anaconda_assistant_conda.config import AssistantCondaConfig

STREAM_RESPONSE = Generator[str, None, None]


def _perform_search(prompt: str, ask_to_login: bool = False) -> STREAM_RESPONSE:
    console.print("[green bold]Hello from Anaconda Assistant![/green bold]")

    config = AssistantCondaConfig()
    session = ChatSession(system_message=config.system_message)
    try:
        _ = session.client.auth_client.account
    except HTTPError as e:
        if e.response.status_code not in [401, 403]:
            raise e

        if not ask_to_login:
            raise SystemExit(1)
        should_do_login = Confirm.ask(
            "You must login to use the assistant. Would you like to login?",
            default=True,
        )
        if should_do_login:
            login()
        else:
            raise SystemExit(1)

    response = cast(STREAM_RESPONSE, session.chat(prompt, stream=True))
    return response


def perform_search(args) -> None:
    full_text = ""
    with Live(
        Markdown(full_text),
        auto_refresh=False,
        vertical_overflow="visible",
        console=console,
    ) as live:
        prompt = f"Find a conda package that can {args.query}"
        response = _perform_search(prompt, ask_to_login=True)
        for chunk in response:
            full_text += chunk
            md = Markdown(full_text)
            live.update(md, refresh=True)
    raise SystemExit(0)


def handle_assistant_subcommands(args) -> None:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(required=True)

    parser_search = subparsers.add_parser(
        "search", help="find a package, using the Anaconda Assistant"
    )
    parser_search.add_argument("query", type=str, help="package search prompt")
    parser_search.set_defaults(func=perform_search)

    args = parser.parse_args(args)
    args.func(args)


@plugins.hookimpl
def conda_subcommands():
    yield plugins.CondaSubcommand(
        name="assist",
        summary="Anaconda Assistant integration",
        action=handle_assistant_subcommands,
    )
