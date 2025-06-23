import typer
import subprocess

from fastmcp import FastMCP, Context
from typing import List, Optional

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
def list_packages() -> str:
    """List all conda packages"""
    # TODO: Implement package listing
    return "Package listing not implemented yet"


@mcp.tool()
def install_package(package_name: str) -> str:
    """Install a conda package"""
    # TODO: Implement package installation
    return f"Package installation not implemented yet: {package_name}"


@mcp.tool()
def uninstall_package(package_name: str) -> str:
    """Uninstall a conda package"""
    # TODO: Implement package uninstallation
    return f"Package uninstallation not implemented yet: {package_name}"


@mcp.tool(
    name="create_environment",
    description="Create a new Conda environment with the specified name, optional python version, and optional packages.",
    input_schema={
        "type": "object",
        "properties": {
            "env_name": {"type": "string", "description": "The name of the new environment."},
            "python_version": {"type": "string", "description": "Python version to install (e.g., '3.11')"},
            "packages": {"type": "array", "items": {"type": "string"}, "description": "Packages to install."},
            "prefix": {"type": "string", "description": "Full path to environment (optional)."}
        },
        "required": ["env_name"]
    }
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
    cmd: List[str] = ["conda", "create", "-y"]
    if prefix:
        cmd += ["--prefix", prefix]
    else:
        cmd += ["--name", env_name]
    if python_version:
        cmd.append(f"python={python_version}")
    if packages:
        cmd.extend(packages)
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        env_path = prefix if prefix else _default_conda_env_path(env_name)
        return env_path
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Conda create failed: {e.stderr}")


@mcp.tool()
def remove_environment(name: str) -> str:
    """Remove a conda environment"""
    # TODO: Implement environment removal
    return f"Environment removal not implemented yet: {name}"


def _default_conda_env_path(env_name: str) -> str:
    import os
    from subprocess import check_output
    envs_dir = check_output(["conda", "info", "--base"], text=True).strip()
    return os.path.join(envs_dir, "envs", env_name)


def main():
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
