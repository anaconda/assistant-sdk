from typing_extensions import Annotated

import typer

from anaconda_cli_base.console import console
from anaconda_cli_base.cli import ErrorHandledGroup
from conda import plugins, CondaError
from conda.exception_handler import ExceptionHandler
from rich.markdown import Markdown
from rich.live import Live
from rich.console import Console

from anaconda_assistant import ChatSession
from anaconda_assistant_conda.config import AssistantCondaConfig


def error_handler(_):
    ExceptionHandler._orig_print_conda_exception = (
        ExceptionHandler._print_conda_exception
    )

    def assistant_exception_handler(self, exc_val: CondaError, exc_tb):
        self._orig_print_conda_exception(exc_val, exc_tb)
        report = self.get_error_report(exc_val, exc_tb)
        command = " ".join(report["command"].split()[1:])

        console.print("[bold green]Hello from Anaconda Assistant![/green bold]")
        session = ChatSession()
        prompt = f"For this conda command\n{command}\nthe following error was reported {exc_val.message}. Suggest how I can change the command to avoid the error."
        response = session.chat(prompt)
        print(response)

    ExceptionHandler._print_conda_exception = assistant_exception_handler


def search(
    query: Annotated[str, typer.Argument(help="A package that can ...")],
) -> None:
    """Ask Anaconda Assistant to find a conda package based on requested capabilities"""
    console.print("[green bold]Hello from Anaconda Assistant![/green bold]")

    full_text = ""
    with Live(
        Markdown(full_text),
        auto_refresh=False,
        vertical_overflow="visible",
        console=console,
    ) as live:
        config = AssistantCondaConfig()
        session = ChatSession(system_message=config.system_message)
        response = session.chat(query, stream=True)

        for chunk in response:
            full_text += chunk
            md = Markdown(full_text)
            live.update(md, refresh=True)
    raise SystemExit(0)


def handle_assistant_subcommands(args) -> None:
    app = typer.Typer(
        help="The conda assistant, powered by Anaconda Assistant",
        add_help_option=True,
        no_args_is_help=True,
        add_completion=False,
        cls=ErrorHandledGroup,
    )

    @app.callback(invoke_without_command=True, no_args_is_help=True)
    def _():
        pass

    app.command(name="search", no_args_is_help=True)(search)

    app(args=args)


@plugins.hookimpl
def conda_subcommands():
    yield plugins.CondaSubcommand(
        name="assist",
        summary="Anaconda Assistant integration",
        action=handle_assistant_subcommands,
    )


def recommend_assist_search(_) -> None:
    console = Console(stderr=True)
    console.print("[bold green]Conda Assistant:[/bold green]")
    console.print("If you're not finding what you're looking for try")
    console.print('  conda assist search "A package that can ..."')


@plugins.hookimpl
def conda_post_commands():
    yield plugins.CondaPostCommand(
        name="assist-search-recommendation",
        action=recommend_assist_search,
        run_for={"search"},
    )


@plugins.hookimpl
def conda_pre_commands():
    yield plugins.CondaPreCommand(
        name="error-handler",
        action=error_handler,
        run_for={
            "create",
            "install",
            "remove",
            "uninstall",
            "update",
            "env_create",
            "env_update",
        },
    )
