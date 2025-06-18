from pprint import pp
import typer
import subprocess
import time
import json

from conda import CondaError, plugins
from conda.cli.conda_argparse import BUILTIN_COMMANDS
from conda.exception_handler import ExceptionHandler
from conda.exceptions import PackagesNotFoundError

from fastmcp import FastMCP, Context
from rich.console import Console


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
def add(a: int, b: int) -> int:
    """Add two numbers"""
    return a + b


@mcp.tool()
def subtract(a: int, b: int) -> int:
    """Subtract two numbers"""
    return a - b


@mcp.tool()
def list_packages() -> str:
    """List all conda packages"""

    try:
        result = subprocess.run(
            ["/opt/anaconda3/bin/conda", "list", "--json"],
            capture_output=True,
            text=True,
            check=True,
        )
        packages = json.loads(result.stdout)
        packages = packages[:10]
        formatted_packages = []
        for package in packages:
            formatted_package = {
                "name": package["name"],
                "version": package["version"],
                "build": package["build_string"],
                "channel": package["channel"],
                # "platform": package["platform"],
                # "build_number": package["build_number"],
                # "base_url": package["base_url"],
                # "dist_name": package["dist_name"]
            }
            formatted_packages.append(formatted_package)
            res = json.dumps(formatted_packages, indent=2)
            print(res)
        return res
    except subprocess.CalledProcessError as e:
        console.print(f"[red]Error running conda list:[/red] {e.stderr}")
        raise SystemExit(1)


@mcp.tool()
def list_pretend_packages() -> str:
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
def sleep_five_seconds() -> str:
    """Sleep for 5 seconds using subprocess"""
    try:
        subprocess.run(["sleep", "5"], check=True)
        print("Slept for 5 seconds")
        return "Slept for 5 seconds"
    except subprocess.CalledProcessError as e:
        console.print(f"[red]Error running sleep:[/red] {e.stderr}")
        raise SystemExit(1)


@mcp.tool()
def list_envs() -> str:
    """List all conda environments"""

    try:
        result = subprocess.run(
            ["/opt/anaconda3/bin/conda", "env", "list", "--json"],
            capture_output=True,
            text=True,
            check=True,
        )

        envs = json.loads(result.stdout)["envs"]
        pp(envs)
        return envs
    except subprocess.CalledProcessError as e:
        console.print(f"[red]Error running conda env list:[/red] {e.stderr}")
        raise SystemExit(1)


from conda.core.envs_manager import list_all_known_prefixes
from .list_env_info import print_env_info


@mcp.tool()
def list_envs_with_details() -> str:
    """List all conda environments with details"""
    print("Available Conda Environments:")
    print("=" * 50)

    # Get all known environment prefixes
    env_prefixes = list_all_known_prefixes()

    if not env_prefixes:
        print("No conda environments found.")
        return

    # Sort environments for consistent output
    env_prefixes = sorted(env_prefixes)

    for i, env_path in enumerate(env_prefixes, 1):
        print_env_info(i, env_path)


if __name__ == "__main__":
    # print("hello")
    list_envs2()
