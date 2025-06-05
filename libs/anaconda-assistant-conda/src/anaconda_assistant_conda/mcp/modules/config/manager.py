# MCP Manager - Client Configuration Manager

import json
from pathlib import Path
from typing import Dict, Any, Optional, List

from anaconda_assistant_conda.mcp.modules.config.registry import ClientRegistry
from anaconda_assistant_conda.mcp.modules.config.utils import read_json_file, write_json_file
from anaconda_assistant_conda.mcp.core.exceptions import ConfigurationError, ClientNotSupportedError

# Define a standard key under which MCP server configurations are stored
# This might need adjustment based on client specifics
MCP_CONFIG_KEY = "mcp.servers"

class ConfigManager:
    """Manages adding/removing MCP server configurations in client JSON files."""

    def __init__(self) -> None:
        self.registry = ClientRegistry()

    def _get_target_config_path(self, client_name: str, workspace_path: Optional[str] = None) -> Path:
        """Helper to get the validated config path."""
        if not self.registry.is_client_supported(client_name):
            raise ClientNotSupportedError(f"Client ","{","client_name","}"," is not supported.")

        config_path = self.registry.get_config_path(client_name, workspace_path)
        if not config_path:
            raise ConfigurationError(f"Could not determine configuration path for client ","{","client_name","}"," ",
                                     f"(workspace: ","{","workspace_path","}",").")
        return config_path

    def add_server_config(self, server_name: str, server_prefix: str, client_name: str, workspace_path: Optional[str] = None) -> None:
        """Adds or updates the configuration for a specific MCP server in the client's JSON config.

        Args:
            server_name: The logical name of the MCP server.
            server_prefix: The installation path (conda environment prefix) of the server.
            client_name: The name of the target MCP client (e.g., 'cursor', 'vscode').
            workspace_path: Optional path to the workspace for workspace-specific config.

        Raises:
            ConfigurationError: If reading/writing the config file fails.
            ClientNotSupportedError: If the client is not supported.
        """
        config_path = self._get_target_config_path(client_name, workspace_path)
        config_data = read_json_file(config_path) or {}

        # Ensure the MCP server list exists
        if MCP_CONFIG_KEY not in config_data:
            config_data[MCP_CONFIG_KEY] = []
        elif not isinstance(config_data[MCP_CONFIG_KEY], list):
            # Handle case where the key exists but is not a list (overwrite or error?)
            print(f"Warning: Overwriting non-list value at key ","{","MCP_CONFIG_KEY","}"," in ","{","config_path","}",".")
            config_data[MCP_CONFIG_KEY] = []

        server_list: List[Dict[str, Any]] = config_data[MCP_CONFIG_KEY]

        # Check if server already exists, update its path if so
        server_found = False
        for server_entry in server_list:
            if isinstance(server_entry, dict) and server_entry.get("name") == server_name:
                server_entry["path"] = server_prefix # Update path
                server_found = True
                break

        # If not found, add a new entry
        if not server_found:
            server_list.append({"name": server_name, "path": server_prefix})

        try:
            write_json_file(config_path, config_data)
            print(f"Configuration for server ","{","server_name","}"," added/updated in ","{","config_path","}",".")
        except IOError as e:
            raise ConfigurationError(f"Failed to write configuration to ","{","config_path","}",": ","{","e","}") from e

    def remove_server_config(self, server_name: str, client_name: str, workspace_path: Optional[str] = None) -> None:
        """Removes the configuration for a specific MCP server from the client's JSON config.

        Args:
            server_name: The logical name of the MCP server to remove.
            client_name: The name of the target MCP client.
            workspace_path: Optional path to the workspace for workspace-specific config.

        Raises:
            ConfigurationError: If reading/writing the config file fails.
            ClientNotSupportedError: If the client is not supported.
        """
        config_path = self._get_target_config_path(client_name, workspace_path)
        config_data = read_json_file(config_path)

        if not config_data or MCP_CONFIG_KEY not in config_data or not isinstance(config_data[MCP_CONFIG_KEY], list):
            print(f"Warning: No server configurations found or key ","{","MCP_CONFIG_KEY","}"," invalid in ","{","config_path","}",". No changes made.")
            return

        server_list: List[Dict[str, Any]] = config_data[MCP_CONFIG_KEY]
        initial_length = len(server_list)

        # Filter out the server entry
        config_data[MCP_CONFIG_KEY] = [entry for entry in server_list if not (isinstance(entry, dict) and entry.get("name") == server_name)]

        if len(config_data[MCP_CONFIG_KEY]) < initial_length:
            try:
                # Write back only if changes were made
                write_json_file(config_path, config_data)
                print(f"Configuration for server ","{","server_name","}"," removed from ","{","config_path","}",".")
            except IOError as e:
                raise ConfigurationError(f"Failed to write updated configuration to ","{","config_path","}",": ","{","e","}") from e
        else:
            print(f"Server ","{","server_name","}"," not found in configuration ","{","config_path","}",". No changes made.")

    def get_installed_servers_from_config(self, client_name: str, workspace_path: Optional[str] = None) -> List[Dict[str, str]]:
        """Reads the client config and returns a list of configured MCP servers.

        Args:
            client_name: The name of the target MCP client.
            workspace_path: Optional path to the workspace for workspace-specific config.

        Returns:
            A list of dictionaries, each containing 'name' and 'path' of a configured server.
        """
        config_path = self._get_target_config_path(client_name, workspace_path)
        config_data = read_json_file(config_path)

        if not config_data or MCP_CONFIG_KEY not in config_data or not isinstance(config_data[MCP_CONFIG_KEY], list):
            return []

        server_list: List[Dict[str, Any]] = config_data[MCP_CONFIG_KEY]
        valid_servers = []
        for entry in server_list:
            if isinstance(entry, dict) and "name" in entry and "path" in entry:
                valid_servers.append({"name": str(entry["name"]), "path": str(entry["path"])})
        return valid_servers


