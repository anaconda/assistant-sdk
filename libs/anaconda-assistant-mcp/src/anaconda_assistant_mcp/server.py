import json
import asyncio
import typer
from typing import Optional, Annotated, List, Union
from pydantic import Field

from fastmcp import FastMCP, Context
from fastmcp.exceptions import ToolError
from conda.api import SubdirData

from .tools_core.list_environment import list_environment_core
from .tools_core.create_environment import create_environment_core
from .tools_core.environment_details import show_environment_details_core
from .tools_core.update_environment import update_environment_core
from .tools_core.remove_environment import remove_environment_core
import ast

mcp: FastMCP = FastMCP("Anaconda Assistant MCP")

helptext = """
The MCP server. \n
See https://github.com/anaconda/assistant-sdk/tree/main/libs/anaconda-assistant-mcp for more information.
"""

mcp_app = typer.Typer(
    help=helptext,
    add_help_option=True,
    add_completion=False,
)


@mcp_app.command(name="serve")
def serve() -> None:
    mcp.run(transport="stdio")

@mcp_app.callback()
def _callback() -> None:
    pass

# ---
# Tools
# ---


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
async def create_environment(
    context: Context,
    env_name: Annotated[str, Field(description="The name of the environment to create. This will be used to generate the environment path if no prefix is specified.")],
    python_version: Annotated[Optional[str], Field(description="Optional Python version specification (e.g., '3.9', '3.10.0'). If not provided, the latest available Python version will be used.")] = None,
    packages: Annotated[Optional[Union[List[str], str]], Field(description="Optional list of package specifications to install in the environment. Each package can include version constraints (e.g., ['numpy>=1.20', 'pandas']). If not provided, only Python will be installed.")] = None,
    prefix: Annotated[Optional[str], Field(description="Optional full path where the environment should be created. If not provided, the environment will be created in the default conda environments directory using the env_name.")] = None
) -> str:
    """
    Create a new conda environment with the specified configuration.
    
    This tool creates a new conda environment using conda's internal APIs. The process involves
    solving package dependencies, downloading packages, and installing them to the target location.
    Progress updates are provided during the creation process.
    
    Returns:
        The full path to the created conda environment.
    
    Raises:
        ToolError: If environment creation fails due to dependency conflicts,
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
    if isinstance(packages, str):
        try:
            import ast
            packages = ast.literal_eval(packages)
        except Exception:
            raise ToolError("Could not parse 'packages' argument as a list.")
    if packages is not None and not isinstance(packages, list):
        packages = [packages]
    try:
        # Report initial progress
        await context.report_progress(
            0,
            100
        )
        
        # Report solving progress
        await context.report_progress(
            25,
            100
        )
        
        env_path = create_environment_core(
            env_name=env_name,
            python_version=python_version,
            packages=packages,
            prefix=prefix
        )
        
        # Report completion
        await context.report_progress(
            100,
            100
        )
        
        return env_path
    except Exception as e:
        # Report error progress
        await context.report_progress(
            100,
            100
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


@mcp.tool(
    name="update_environment",
    description="Update an existing Conda environment by adding or updating packages. Specify env_name or prefix."
)
async def update_environment(
    packages: Annotated[Union[List[str], str], Field(description="List of packages to update/install.")],
    env_name: Optional[str] = None,
    prefix: Optional[str] = None
) -> str:
    if isinstance(packages, str):
        import ast
        try:
            packages = ast.literal_eval(packages)
        except Exception:
            raise RuntimeError("Could not parse 'packages' argument as a list.")
    if not isinstance(packages, list):
        packages = [packages]
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
async def remove_environment(
    env_name: Annotated[Optional[str], Field(description="The name of the environment to remove.")] = None,
    prefix: Annotated[Optional[str], Field(description="The full path to the environment to remove (used instead of name).")] = None
) -> str:
    """
    Remove a conda environment using conda's internal APIs.
    
    This tool removes a conda environment by unregistering it from conda's
    environment list and deleting the environment directory.
    
    Args:
        env_name: Optional name of the environment to remove
        prefix: Optional full path to the environment to remove
        
    Returns:
        The full path to the removed environment
        
    Raises:
        ToolError: If environment removal fails due to missing environment,
                  permission issues, or other errors.
    
    Example:
        Remove environment by name:
        >>> remove_environment("myenv")
        
        Remove environment by path:
        >>> remove_environment(prefix="/path/to/environment")
    """
    try:
        env_path = remove_environment_core(
            env_name=env_name,
            prefix=prefix
        )
        return env_path
    except Exception as e:
        # Provide more descriptive error messages based on the exception type
        error_msg = str(e)
        
        # Check for common conda-specific error patterns
        if "Cannot remove the base environment" in error_msg:
            reason = "Cannot remove the base environment - this is a protected environment"
        elif "Environment does not exist" in error_msg:
            reason = "Environment does not exist - check the environment name or path"
        elif "permission" in error_msg.lower() or "access" in error_msg.lower():
            reason = "Permission denied - check if you have write access to the environment location"
        elif "directory not empty" in error_msg.lower():
            reason = "Environment directory could not be removed - some files may be in use"
        else:
            reason = "Unexpected error during environment removal"
        
        raise ToolError(
            f"Failed to remove conda environment: {reason}. "
            f"Error details: {error_msg}"
        )


@mcp.tool()
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
