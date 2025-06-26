import json
import asyncio
import typer

from typing import List, Optional
from fastmcp import FastMCP, Context
from conda.api import SubdirData

from .tools_core.list_environment import list_environment_core
from .tools_core.create_environment import create_environment_core

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
async def install_package(package_name: str) -> str:
    """Install a conda package"""
    # TODO: Implement package installation
    return f"Package installation not implemented yet: {package_name}"


@mcp.tool()
async def uninstall_package(package_name: str) -> str:
    """Uninstall a conda package"""
    # TODO: Implement package uninstallation
    return f"Package uninstallation not implemented yet: {package_name}"


@mcp.tool(
    name="create_environment",
    description="Create a new Conda environment with the specified name, optional python version, and optional packages."
)
async def create_environment(
    env_name: str,
    python_version: Optional[str] = None,
    packages: Optional[List[str]] = None,
    prefix: Optional[str] = None
) -> str:
    """
    Create a new conda environment with the given name, python version, and packages.
    Returns the full path to the created environment.
    """
    try:
        env_path = create_environment_core(
            env_name=env_name,
            python_version=python_version,
            packages=packages,
            prefix=prefix
        )
        return env_path
    except Exception as e:
        # Provide more descriptive error messages based on the exception type
        error_msg = str(e)
        
        # Check for common conda-specific error patterns
        if "UnsatisfiableError" in error_msg or "solving environment" in error_msg.lower():
            reason = "Package dependency conflicts or unsatisfiable requirements"
        elif "PackagesNotFoundError" in error_msg or "packages are missing" in error_msg.lower():
            reason = "One or more packages not found in available channels"
        elif "permission" in error_msg.lower() or "access" in error_msg.lower():
            reason = "Permission denied - check if you have write access to the environment location"
        elif "network" in error_msg.lower() or "connection" in error_msg.lower():
            reason = "Network connectivity issue - check your internet connection and conda channels"
        elif "disk space" in error_msg.lower() or "no space" in error_msg.lower():
            reason = "Insufficient disk space for environment creation"
        elif "environment already exists" in error_msg.lower():
            reason = "Environment already exists - consider using a different name or removing the existing environment"
        else:
            reason = "Unexpected error during environment creation"
        
        raise RuntimeError(
            f"Failed to create conda environment '{env_name}': {reason}. "
            f"Error details: {error_msg}"
        )


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


@mcp.tool()
async def list_environment() -> str:
    """List all conda environments"""
    return json.dumps(list_environment_core(), indent=2)


async def main() -> None:
    mcp.run(transport="stdio")


if __name__ == "__main__":
    asyncio.run(main())
