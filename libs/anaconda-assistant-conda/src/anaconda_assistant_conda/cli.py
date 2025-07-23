import sys

import typer
from rich.console import Console
from typing_extensions import Annotated

import asyncio
from fastmcp import Client

from .prompt_debug_config import prompt_debug_config
from .config import AssistantCondaConfig

console = Console()

helptext = """
The conda assistant, powered by Anaconda Assistant. \n
See https://anaconda.com/docs/tools/working-with-conda/cli-assistant for more information.
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
    prompt_debug_config()


@app.command(name="configure")
def configure() -> None:
    console.print(
        "[yellow]Warning: The 'configure' command is deprecated and will be removed in a future version. Please use `conda assist config`.[/yellow]"
    )
    prompt_debug_config()


@app.command(name="mcp")
def mcp(prompt: str) -> None:
    """Send a prompt to an already-running MCP server and print the response."""
    async def run() -> None:
        async with Client(transport="stdio") as client:
            # Call the list_environment tool as a test
            try:
                result = await client.call_tool("list_environment", {})
                print(result[0].text if result else "No response from server.")
            except Exception as e:
                print(f"Error communicating with MCP server: {e}")
    asyncio.run(run())
