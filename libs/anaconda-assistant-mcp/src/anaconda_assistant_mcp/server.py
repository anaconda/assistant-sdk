import typer
import asyncio

from fastmcp import FastMCP, Context

mcp = FastMCP("Anaconda Assistant MCP")

# ---
# CLI conda plugin setup
# ---

helptext = """
The MCP server. \n
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


def main():
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
