# MCP Manager - Conda Utilities

import subprocess
import json
import os
from typing import List, Dict, Any, Optional
from anaconda_assistant_conda.mcp.core.exceptions import (
    CondaCommandError,
    EnvironmentCreationError,
    EnvironmentRemovalError,
    PackageInstallationError,
    PackageUpdateError
)

def run_conda_command(command: List[str], env: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
    """Runs a conda command using subprocess and returns the JSON output.

    Args:
        command: A list of strings representing the conda command and its arguments.
                 Must include '--json' for JSON output.
        env: Optional environment variables for the subprocess.

    Returns:
        A dictionary parsed from the JSON output of the conda command.

    Raises:
        CondaCommandError: If the command fails or returns non-JSON output.
    """
    if "--json" not in command:
        raise ValueError("Conda commands must include '--json' for parsing.")

    try:
        # Execute the conda command
        process = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=False,  # We check the return code manually
            env=env or os.environ.copy()
        )
    except FileNotFoundError:
        # Handle case where conda executable is not found
        raise CondaCommandError(
            command=" ".join(command),
            return_code=-1,
            stdout="",
            stderr="'conda' command not found. Is conda installed and in the PATH?"
        )
    except Exception as e:
        # Catch other potential subprocess errors during execution itself
        raise CondaCommandError(
            command=" ".join(command),
            return_code=-1,
            stdout="",
            stderr=f"An unexpected error occurred during subprocess execution: {e}"
        )

    # Process the result after execution
    stdout = process.stdout.strip()
    stderr = process.stderr.strip()

    # Check if the command failed based on return code
    if process.returncode != 0:
        raise CondaCommandError(
            command=" ".join(command),
            return_code=process.returncode,
            stdout=stdout, # Include stdout for context
            stderr=stderr  # stderr should contain the actual error from conda
        )

    # Command succeeded (returncode 0), now parse JSON
    # Find the start of the JSON object ('{') to handle potential plugin output
    json_start_index = stdout.find('{')
    if json_start_index == -1:
        # Command succeeded but no JSON object found in output
        raise CondaCommandError(
            command=" ".join(command),
            return_code=process.returncode,
            stdout=stdout,
            stderr="Conda command succeeded but no JSON object found in output."
        )

    # Slice the stdout string from the first brace onwards
    json_string = stdout[json_start_index:]
    try:
        result = json.loads(json_string)
        return result
    except json.JSONDecodeError as e:
        # Command succeeded, JSON started, but parsing failed
        raise CondaCommandError(
            command=" ".join(command),
            return_code=process.returncode,
            stdout=stdout, # Show the full stdout for debugging
            stderr=f"Failed to decode JSON output: {e}. Raw JSON string attempted: {json_string[:100]}..."
        )

def get_conda_info() -> Dict[str, Any]:
    """Retrieves conda information using 'conda info --json'."""
    command = ["conda", "info", "--json"]
    return run_conda_command(command)

def list_environments() -> Dict[str, str]:
    """Lists all conda environments and their paths."""
    info = get_conda_info()
    envs = info.get("envs", [])
    env_dict = {}
    base_prefix = info.get("conda_prefix")
    if base_prefix:
        env_dict["base"] = base_prefix
    for env_path in envs:
        if env_path != base_prefix:
            env_name = os.path.basename(env_path)
            env_dict[env_name] = env_path
    return env_dict

def create_environment(prefix: str, packages: Optional[List[str]] = None, channel: Optional[str] = None) -> Dict[str, Any]:
    """Creates a new conda environment.

    Args:
        prefix: The absolute path (prefix) where the environment should be created.
        packages: A list of packages to install during creation.
        channel: An optional channel to use for package installation.

    Returns:
        Parsed JSON output from the conda create command.
    """
    # Removed --quiet based on previous debugging steps
    command = ["conda", "create", "--prefix", prefix, "--yes", "--json"]
    if channel:
        command.extend(["-c", channel])
    if packages:
        command.extend(packages)
    else: # Ensure at least python is installed if no packages specified
        command.append("python")

    try:
        return run_conda_command(command)
    except CondaCommandError as e:
        # Add context to the error
        raise EnvironmentCreationError(f"Failed to create environment at {prefix}: {e}") from e

def remove_environment(prefix: str) -> Dict[str, Any]:
    """Removes a conda environment.

    Args:
        prefix: The absolute path (prefix) of the environment to remove.

    Returns:
        Parsed JSON output from the conda remove command.
    """
    # Removed --quiet based on previous debugging steps
    command = ["conda", "remove", "--prefix", prefix, "--all", "--yes", "--json"]
    try:
        return run_conda_command(command)
    except CondaCommandError as e:
        raise EnvironmentRemovalError(f"Failed to remove environment at {prefix}: {e}") from e

def install_packages(prefix: str, packages: List[str], channel: Optional[str] = None) -> Dict[str, Any]:
    """Installs packages into a specific conda environment.

    Args:
        prefix: The absolute path (prefix) of the target environment.
        packages: A list of packages to install.
        channel: An optional channel to use.

    Returns:
        Parsed JSON output from the conda install command.
    """
    # Removed --quiet based on previous debugging steps
    command = ["conda", "install", "--prefix", prefix, "--yes", "--json"]
    if channel:
        command.extend(["-c", channel])
    command.extend(packages)

    try:
        return run_conda_command(command)
    except CondaCommandError as e:
        raise PackageInstallationError(f"Failed to install packages into {prefix}: {e}") from e

def update_packages(prefix: str, packages: Optional[List[str]] = None, update_all: bool = False) -> Dict[str, Any]:
    """Updates packages in a specific conda environment.

    Args:
        prefix: The absolute path (prefix) of the target environment.
        packages: A list of specific packages to update. If None and update_all is False, updates conda itself.
        update_all: If True, updates all packages in the environment.

    Returns:
        Parsed JSON output from the conda update command.
    """
    # Removed --quiet based on previous debugging steps
    command = ["conda", "update", "--prefix", prefix, "--yes", "--json"]
    if update_all:
        command.append("--all")
    elif packages:
        command.extend(packages)
    # If neither packages nor update_all is specified, conda update defaults to updating conda itself.

    try:
        return run_conda_command(command)
    except CondaCommandError as e:
        raise PackageUpdateError(f"Failed to update packages in {prefix}: {e}") from e


