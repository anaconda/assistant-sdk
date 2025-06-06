import typer
from mcp.server.fastmcp import FastMCP, Context
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


@mcp.tool()
def list_packages() -> None:
    """List all conda packages"""

    import subprocess

    try:
        result = subprocess.run(
            ["conda", "list"], capture_output=True, text=True, check=True
        )
        console.print(result.stdout)
    except subprocess.CalledProcessError as e:
        console.print(f"[red]Error running conda list:[/red] {e.stderr}")
        raise SystemExit(1)

    console.print("[green bold]Hello from Anaconda Assistant![/green bold]")


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
