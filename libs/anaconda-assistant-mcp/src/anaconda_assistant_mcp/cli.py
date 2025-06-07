import typer
from fastmcp import FastMCP, Context
from rich.console import Console

console = Console()
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


@mcp_app.command(name="list")
@mcp.tool()
def list_packages() -> None:
    """List all conda packages"""

    import subprocess

    try:
        result = subprocess.run(
            ["conda", "list"], capture_output=True, text=True, check=True
        )
        console.print(result.stdout)
        return result.stdout
    except subprocess.CalledProcessError as e:
        console.print(f"[red]Error running conda list:[/red] {e.stderr}")
        raise SystemExit(1)


@mcp_app.command(name="list-pretend")
@mcp.tool()
def list_pretend_packages() -> None:
    """List all conda packages"""

    import os
    import json

    console.print("Here we go.... 📁")
    conda_list_file = os.path.join(os.path.dirname(__file__), "conda-list.txt")
    console.print(conda_list_file)

    with open(conda_list_file, "r") as f:
        conda_list = f.read()

    console.print(conda_list)

    return conda_list


@mcp.tool()
def list_envs() -> None:
    """List all conda environments"""
    import subprocess

    try:
        result = subprocess.run(
            ["conda", "env", "list"], capture_output=True, text=True, check=True
        )
        console.print(result.stdout)
    except subprocess.CalledProcessError as e:
        console.print(f"[red]Error running conda env list:[/red] {e.stderr}")
        raise SystemExit(1)
