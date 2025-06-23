from pprint import pp
import typer
import subprocess
import time
import json
import asyncio
import json

from conda import CondaError, plugins
from conda.cli.conda_argparse import BUILTIN_COMMANDS
from conda.exception_handler import ExceptionHandler
from conda.exceptions import PackagesNotFoundError

from fastmcp import FastMCP, Context
from rich.console import Console

from .list_env_info import list_envs


console = Console()
mcp = FastMCP("Anaconda Assistant MCP")

helptext = """
The conda assistant, powered by Anaconda Assistant. \n
See https://anaconda.github.io/assistant-sdk/ for more information.
"""

mcp_app_experiments = typer.Typer(
    help=helptext,
    add_help_option=True,
    no_args_is_help=True,
    add_completion=False,
)


@mcp_app_experiments.callback(invoke_without_command=True, no_args_is_help=True)
def _() -> None:
    pass


@mcp_app_experiments.command(name="serve")
def serve() -> None:
    mcp.run(transport="stdio")


# ---
# Tools
# ---


@mcp.tool()
async def add(a: int, b: int) -> int:
    """Add two numbers"""
    return a + b


@mcp.tool()
async def subtract(a: int, b: int) -> int:
    """Subtract two numbers"""
    return a - b


@mcp.tool()
async def list_packages() -> str:
    """List all conda packages using the conda package"""
    try:
        from conda.api import list_packages
        from conda.base.context import context

        # Get packages from the current environment
        packages = list_packages(context.prefix)

        # Format the packages for output
        formatted_packages = []
        for package in packages:
            formatted_package = {
                "name": package.name,
                "version": package.version,
                "build": package.build_string,
                "channel": package.channel.name if package.channel else None,
            }
            formatted_packages.append(formatted_package)

        # Limit to first 10 packages for readability
        formatted_packages = formatted_packages[:10]

        result = json.dumps(formatted_packages, indent=2)
        print(result)
        return result

    except Exception as e:
        console.print(f"[red]Error listing packages with conda API:[/red] {e}")
        raise SystemExit(1)


@mcp.tool()
async def list_pretend_packages() -> str:
    """List all conda packages"""

    conda_list = """# packages in environment at /opt/anaconda3 🫨 5 seconds:
#
# Name                             Version              Build                Channel
aext-assistant                     4.20.0               py313hca03da5_jl4_0
aext-assistant-server              4.20.0               py313hca03da5_0
aext-core                          4.20.0               py313hca03da5_jl4_0
aext-core-server                   4.20.0               py313hca03da5_0
aext-environments-server           4.20.0               py313hca03da5_0
aext-panels                        4.20.0               py313hca03da5_0
aext-panels-server                 4.20.0               py313hca03da5_0
aext-project-filebrowser-server    4.20.0               py313hb41f31a_0
"""

    # try:
    #     result = subprocess.run(
    #         ["/opt/anaconda3/bin/conda", "list"],
    #         capture_output=True,
    #         text=True,
    #         check=True,
    #     )
    #     print(result.stdout)
    #     return result.stdout
    # except subprocess.CalledProcessError as e:
    #     raise SystemExit(1)

    # time.sleep(5)  # Add a 5 second delay

    print(conda_list)

    return conda_list


@mcp.tool()
async def sleep_five_seconds() -> str:
    """Sleep for 5 seconds using subprocess"""
    try:
        subprocess.run(["sleep", "5"], check=True)
        print("Slept for 5 seconds")
        return "Slept for 5 seconds"
    except subprocess.CalledProcessError as e:
        console.print(f"[red]Error running sleep:[/red] {e.stderr}")
        raise SystemExit(1)


@mcp.tool()
async def list_envs_old() -> str:
    """List all conda environments"""

    result = subprocess.run(
        ["/opt/anaconda3/bin/conda", "env", "list", "--json"],
        capture_output=True,
        text=True,
        check=True,
    )

    envs = json.loads(result.stdout)["envs"]
    return envs


@mcp.tool()
async def list_envs() -> str:
    """List all conda environments with details"""
    return json.dumps(list_envs(), indent=2)


async def main():
    """Run the MCP server"""
    res = await list_envs_with_details()
    print(res)


if __name__ == "__main__":
    asyncio.run(main())
