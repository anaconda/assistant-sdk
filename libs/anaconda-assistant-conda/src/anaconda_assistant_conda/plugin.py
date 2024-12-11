from typing_extensions import Annotated

import typer
from anaconda_cli_base.cli import ErrorHandledGroup
from conda import plugins, CondaError
from conda.exception_handler import ExceptionHandler
from rich.markdown import Markdown
from rich.live import Live
from rich.console import Console

from anaconda_assistant import ChatSession
from anaconda_assistant_conda.config import AssistantCondaConfig

console = Console()


def _stream_response(system_message, prompt) -> None:
    fake_app = typer.Typer(
        help="fake app to support error handling", cls=ErrorHandledGroup
    )

    @fake_app.callback(name="chat", invoke_without_command=True, cls=ErrorHandledGroup)
    def chat(
        system_message: Annotated[str, typer.Argument],
        prompt: Annotated[str, typer.Argument],
    ):
        full_text = ""
        with Live(
            Markdown(full_text),
            auto_refresh=False,
            vertical_overflow="visible",
            console=console,
        ) as live:
            session = ChatSession(system_message=system_message)
            response = session.chat(prompt, stream=True)

            for chunk in response:
                full_text += chunk
                md = Markdown(full_text)
                live.update(md, refresh=True)

    fake_app(args=(system_message, prompt))


def error_handler(_) -> None:
    config = AssistantCondaConfig()
    if not config.suggest_correction_on_error:
        return

    ExceptionHandler._orig_print_conda_exception = (
        ExceptionHandler._print_conda_exception
    )

    def assistant_exception_handler(self, exc_val: CondaError, exc_tb):
        self._orig_print_conda_exception(exc_val, exc_tb)
        if exc_val.return_code == 0:
            return

        report = self.get_error_report(exc_val, exc_tb)

        console.print("[bold green]Hello from Anaconda Assistant![/green bold]")
        console.print("I'm going to help you diagnose and correct this error.")
        prompt = f"COMMAND:\n{report['command']}\nMESSAGE:\n{report['error']}"
        _stream_response(config.system_messages.error, prompt)

    ExceptionHandler._print_conda_exception = assistant_exception_handler


def search(
    query: Annotated[str, typer.Argument(help="A package that can ...")],
) -> None:
    """Ask Anaconda Assistant to find a conda package based on requested capabilities"""
    console.print("[green bold]Hello from Anaconda Assistant![/green bold]")

    config = AssistantCondaConfig()
    _stream_response(config.system_messages.search, query)
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
