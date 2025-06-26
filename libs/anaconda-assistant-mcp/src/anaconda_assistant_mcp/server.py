import typer
import json
import asyncio
from typing import Optional, Annotated
from pydantic import Field

from fastmcp import FastMCP, Context
from conda.api import SubdirData

from .tools_core.list_environment import list_environment_core
from .tools_core.environment_details import show_environment_details_core
from .tools_core.update_environment import update_environment_core

mcp: FastMCP = FastMCP("Anaconda Assistant MCP")

helptext = """
The MCP server. \n
See https://github.com/anaconda/assistant-sdk/tree/main/libs/anaconda-assistant-mcp for more information.
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


@mcp_app.command(name="serve")
def serve() -> None:
    mcp.run(transport="stdio")


# ---
# Tools
# ---


@mcp.tool()
async def list_packages() -> str:
    """List all conda packages"""
    # TODO: Implement package listing
    return "Package listing not implemented yet"


@mcp.tool()
async def create_environment(name: str, python_version: str = "3.10") -> str:
    """Create a new conda environment"""
    # TODO: Implement environment creation
    return (
        f"Environment creation not implemented yet: {name} with Python {python_version}"
    )


@mcp.tool()
async def remove_environment(name: str) -> str:
    """Remove a conda environment"""
    # TODO: Implement environment removal
    return f"Environment removal not implemented yet: {name}"


@mcp.tool()
async def list_environment() -> str:
    """List all conda environments"""
    return json.dumps(list_environment_core(), indent=2)


@mcp.tool()
async def show_environment_details(
    env_name: Annotated[Optional[str], Field(description="The name of the environment to inspect.")] = None,
    prefix: Annotated[Optional[str], Field(description="The full path to the environment (used instead of name).")] = None
) -> str:
    """Show installed packages and metadata for a given Conda environment."""
    return json.dumps(show_environment_details_core(env_name=env_name, prefix=prefix), indent=2)


@mcp.tool()
async def install_package(package_name: str) -> str:
    """Install a conda package"""
    # TODO: Implement package installation
    return f"Package installation not implemented yet: {package_name}"


@mcp.tool()
async def uninstall_package(package_name: str) -> str:
    """Uninstall a conda package"""
    # TODO: Implement package uninstallation
    return f"Package uninstallation not implemented yet: {package_name}"


@mcp.tool()
async def create_environment(name: str, python_version: str = "3.10") -> str:
    """Create a new conda environment"""
    # TODO: Implement environment creation
    return (
        f"Environment creation not implemented yet: {name} with Python {python_version}"
    )


@mcp.tool(
    name="update_environment",
    description="Update an existing Conda environment by adding or updating packages. Specify env_name or prefix."
)
async def update_environment(
    packages: list[str],
    env_name: str = None,
    prefix: str = None
) -> str:
    """
    Update an existing conda environment (by name or prefix) by installing/updating packages.
    Returns the full path to the updated environment.
    """
    if not packages:
        raise ValueError("Must specify at least one package to update/install.")

    try:
        env_path = update_environment_core(
            packages=packages,
            env_name=env_name,
            prefix=prefix
        )
        return env_path
    except Exception as e:
        raise RuntimeError(f"Conda update failed: {str(e)}")


@mcp.tool()
async def remove_environment(name: str) -> str:
    """Remove a conda environment"""
    # TODO: Implement environment removal
    return f"Environment removal not implemented yet: {name}"


@mcp.tool(
    name="search_packages",
    description="Search for available Conda packages matching a query string.",
)
async def search_packages(
    package_name: str, channel: Optional[str] = None, platform: Optional[str] = None
) -> list[str]:
    """Search available conda packages matching the given package_name: channel, and platform."""
    return [
        str(match)
        for match in SubdirData.query_all(
            package_name,
            channels=[channel] if channel else None,
            subdirs=[platform] if platform else None,
        )
    ]


# ---
# Main
# ---


async def main() -> None:
    mcp.run(transport="stdio")


if __name__ == "__main__":
    asyncio.run(main())
