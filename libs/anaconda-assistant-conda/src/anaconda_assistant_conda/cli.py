import typer
from anaconda_cli_base.cli import ErrorHandledGroup
from anaconda_cli_base.console import console
from typing_extensions import Annotated

from .config import AssistantCondaConfig
from .core import stream_response


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


@app.command(name="search", no_args_is_help=True)
def search(
    query: Annotated[str, typer.Argument(help="A package that can ...")],
) -> None:
    """Ask Anaconda Assistant to find a conda package based on requested capabilities"""
    console.print("[green bold]Hello from Anaconda Assistant![/green bold]")

    config = AssistantCondaConfig()
    stream_response(system_message=config.system_messages.search, prompt=query)
    raise SystemExit(0)
