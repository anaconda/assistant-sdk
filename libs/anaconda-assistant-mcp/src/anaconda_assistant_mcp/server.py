import json
import asyncio
import typer

from typing import List, Optional
from fastmcp import FastMCP, Context
from fastmcp.exceptions import ToolError
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


@mcp.tool()
async def create_environment(
    env_name: str,
    python_version: Optional[str] = None,
    packages: Optional[List[str]] = None,
    prefix: Optional[str] = None
) -> str:
    """
    Create a new conda environment with the specified configuration.
    
    This tool creates a new conda environment using conda's internal APIs. The process involves
    solving package dependencies, downloading packages, and installing them to the target location.
    Progress updates are provided during the creation process.
    
    Args:
        env_name: The name of the environment to create. This will be used to generate
                 the environment path if no prefix is specified.
        python_version: Optional Python version specification (e.g., "3.9", "3.10.0").
                       If not provided, the latest available Python version will be used.
        packages: Optional list of package specifications to install in the environment.
                 Each package can include version constraints (e.g., ["numpy>=1.20", "pandas"]).
                 If not provided, only Python will be installed.
        prefix: Optional full path where the environment should be created.
               If not provided, the environment will be created in the default conda
               environments directory using the env_name.
    
    Returns:
        The full path to the created conda environment.
    
    Raises:
        RuntimeError: If environment creation fails due to dependency conflicts,
                     missing packages, permission issues, or other errors.
    
    Example:
        Create a basic Python environment:
        >>> create_environment("myenv")
        
        Create environment with specific Python version:
        >>> create_environment("myenv", python_version="3.9")
        
        Create environment with packages:
        >>> create_environment("myenv", packages=["numpy", "pandas>=1.3"])
        
        Create environment in custom location:
        >>> create_environment("myenv", prefix="/custom/path/myenv")
    """
    try:
        # Report initial progress
        await mcp.report_progress(
            "Starting conda environment creation...",
            percentage=0
        )
        
        # Report solving progress
        await mcp.report_progress(
            "Solving package dependencies...",
            percentage=25
        )
        
        env_path = create_environment_core(
            env_name=env_name,
            python_version=python_version,
            packages=packages,
            prefix=prefix
        )
        
        # Report completion
        await mcp.report_progress(
            f"Environment '{env_name}' created successfully at {env_path}",
            percentage=100
        )
        
        return env_path
    except Exception as e:
        # Report error progress
        await mcp.report_progress(
            f"Environment creation failed: {str(e)}",
            percentage=100
        )
        
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
        
        raise ToolError(
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
