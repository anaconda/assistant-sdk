# MCP Manager - Environment Module

import os
from typing import List, Dict, Optional
from anaconda_assistant_conda.mcp.settings import get_settings
from anaconda_assistant_conda.mcp.modules import conda_utils
# Import specific exceptions directly
from anaconda_assistant_conda.mcp.core.exceptions import EnvironmentCreationError, EnvironmentRemovalError

class EnvironmentManager:
    """Manages conda environments specifically for MCP servers."""

    def __init__(self) -> None:
        self.settings = get_settings()
        self.mcp_base_dir = self.settings.mcp_environment_path
        # Ensure the base directory exists
        os.makedirs(self.mcp_base_dir, exist_ok=True)

    def get_environment_prefix(self, server_name: str) -> str:
        """Constructs the expected environment path for a given server name."""
        return os.path.join(self.mcp_base_dir, server_name)

    def environment_exists(self, server_name: str) -> bool:
        """Checks if a dedicated environment exists for the server."""
        prefix = self.get_environment_prefix(server_name)
        return os.path.isdir(prefix)

    def create_environment(self, server_name: str, packages: Optional[List[str]] = None, channel: Optional[str] = None) -> str:
        """Creates a dedicated conda environment for the MCP server.

        Args:
            server_name: The name of the MCP server.
            packages: Optional list of packages to install during creation.
            channel: Optional channel to use.

        Returns:
            The prefix path of the created environment.

        Raises:
            EnvironmentCreationError: If the environment already exists or creation fails.
        """
        prefix = self.get_environment_prefix(server_name)
        if self.environment_exists(server_name):
            # Or potentially log a warning and return the existing prefix?
            # For now, strict error if trying to create over existing.
            raise EnvironmentCreationError(f"Environment for server {server_name} already exists at {prefix}.")

        print(f"Creating environment for {server_name} at {prefix}...")
        try:
            conda_utils.create_environment(prefix=prefix, packages=packages, channel=channel)
            print(f"Environment {server_name} created successfully.")
            return prefix
        except Exception as e:
            # Catch specific conda errors if needed, re-raise as EnvironmentCreationError
            raise EnvironmentCreationError(f"Failed to create environment for {server_name}: {e}") from e

    def remove_environment(self, server_name: str) -> None:
        """Removes the dedicated conda environment for the MCP server.

        Args:
            server_name: The name of the MCP server.

        Raises:
            EnvironmentRemovalError: If the environment doesn't exist or removal fails.
        """
        prefix = self.get_environment_prefix(server_name)
        if not self.environment_exists(server_name):
            raise EnvironmentRemovalError(f"Environment for server {server_name} not found at {prefix}.")

        print(f"Removing environment for {server_name} at {prefix}...")
        try:
            conda_utils.remove_environment(prefix=prefix)
            print(f"Environment {server_name} removed successfully.")
        except Exception as e:
            raise EnvironmentRemovalError(f"Failed to remove environment for {server_name}: {e}") from e

    def list_installed_environments(self) -> Dict[str, str]:
        """Lists all environments managed by MCP Manager within its base directory."""
        installed_envs: Dict[str, str] = {}
        if not os.path.isdir(self.mcp_base_dir):
            return installed_envs

        for item in os.listdir(self.mcp_base_dir):
            item_path = os.path.join(self.mcp_base_dir, item)
            # Basic check: is it a directory and does it look like a conda env (e.g., has conda-meta)?
            conda_meta_path = os.path.join(item_path, "conda-meta")
            if os.path.isdir(item_path) and os.path.isdir(conda_meta_path):
                installed_envs[item] = item_path
        return installed_envs


