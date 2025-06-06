import typer
from mcp.server.fastmcp import FastMCP, Context

mcp = FastMCP("Anaconda Assistant MCP")

helptext = """
The conda assistant, powered by Anaconda Assistant. \n
See https://anaconda.github.io/assistant-sdk/ for more information.
"""

mcp_app = typer.Typer(
    help=helptext,
    add_help_option=True,
    no_args_is_help=True,
    add_completion=False,
)


@mcp_app.callback(invoke_without_command=True, no_args_is_help=True)
def _() -> None:
    pass


@mcp_app.command(name="server-start")
def server_start() -> None:
    mcp.run()


@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers"""
    return a + b


@mcp.tool()
def subtract(a: int, b: int) -> int:
    """Subtract two numbers"""
    return a - b
