import sys

import typer
from rich.console import Console
from typing_extensions import Annotated

from .debug_config import debug_config
from .config import AssistantCondaConfig
from .core import stream_response

console = Console()

helptext = """
The conda assistant, powered by Anaconda Assistant. \n
See https://anaconda.github.io/assistant-sdk/ for more information.
"""

app = typer.Typer(
    help=helptext,
    add_help_option=True,
    no_args_is_help=True,
    add_completion=False,
)


@app.callback(invoke_without_command=True, no_args_is_help=True)
def _() -> None:
    pass


@app.command(name="config")
def config() -> None:
    debug_config()


@app.command(name="configure")
def configure() -> None:
    console.print(
        "[yellow]Warning: The 'configure' command is deprecated and will be removed in a future version. Please use `conda assist config`.[/yellow]"
    )
    debug_config()
