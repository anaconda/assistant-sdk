# MCP Manager - Client Configuration Registry

import os
from typing import Dict, Optional
from pathlib import Path

# Define known client identifiers and their default configuration file locations
# Paths are relative to the user's home directory or standard config locations.
# This needs careful verification based on actual client implementations.
CLIENT_CONFIG_PATHS: Dict[str, Dict[str, Optional[str]]] = { # Added type hint
    "cursor": {
        "global": os.path.join("~", ".cursor", "settings.json"),
        # Workspace config is usually relative to the workspace folder, handled dynamically
        "workspace_file": ".cursor-workspace.json" # Example filename
    },
    "vscode": {
        # VS Code settings can be complex (User, Workspace, Workspace Folder)
        # Targeting User settings for global, workspace for local
        "global": os.path.join("~", "AppData", "Roaming", "Code", "User", "settings.json"), # Windows example
        # Add paths for macOS and Linux
        "global_macos": os.path.join("~", "Library", "Application Support", "Code", "User", "settings.json"),
        "global_linux": os.path.join("~", ".config", "Code", "User", "settings.json"),
        "workspace_file": os.path.join(".vscode", "settings.json")
    },
    "claude-desktop": {
        "global": os.path.join("~", ".claude", "config.json"), # Hypothetical
        "workspace_file": None # Assuming no workspace config
    },
    # Add other clients as needed
}

class ClientRegistry:
    """Provides information about known MCP clients and their configuration paths."""

    def is_client_supported(self, client_name: str) -> bool:
        """Checks if the given client name is known."""
        return client_name.lower() in CLIENT_CONFIG_PATHS

    def get_global_config_path(self, client_name: str) -> Optional[Path]:
        """Gets the default global configuration file path for a client.

        Handles OS differences for clients like VS Code.
        Returns None if the client is not supported or has no global config.
        """
        client_name = client_name.lower()
        if not self.is_client_supported(client_name):
            return None

        paths: Dict[str, Optional[str]] = CLIENT_CONFIG_PATHS[client_name]
        global_path_str = None

        if client_name == "vscode":
            if os.name == "nt": # Windows
                global_path_str = paths.get("global")
            elif os.uname().sysname == "Darwin": # macOS
                global_path_str = paths.get("global_macos")
            else: # Linux/Other
                global_path_str = paths.get("global_linux")
        else:
            global_path_str = paths.get("global")

        if global_path_str:
            return Path(os.path.expanduser(global_path_str))
        return None

    def get_workspace_config_filename(self, client_name: str) -> Optional[str]:
        """Gets the expected filename for workspace-specific configuration.

        Returns None if the client doesn't support workspace config or is unknown.
        """
        client_name = client_name.lower()
        if not self.is_client_supported(client_name):
            return None
        # Explicitly type the inner dictionary to help mypy
        client_paths: Dict[str, Optional[str]] = CLIENT_CONFIG_PATHS[client_name]
        return client_paths.get("workspace_file")

    def get_config_path(self, client_name: str, workspace_path: Optional[str] = None) -> Optional[Path]:
        """Determines the target configuration file path (global or workspace).

        Args:
            client_name: The name of the MCP client.
            workspace_path: Optional path to the workspace directory.

        Returns:
            The Path object for the target config file, or None if not applicable.
        """
        client_name = client_name.lower()
        if not self.is_client_supported(client_name):
            return None

        if workspace_path:
            workspace_filename = self.get_workspace_config_filename(client_name)
            if workspace_filename:
                return Path(os.path.expanduser(workspace_path)) / workspace_filename
            else:
                # Client doesn't support workspace config, fall back to global or raise error?
                # For now, fall back to global if workspace specified but not supported.
                print(f"Warning: Client ","{","client_name","}"," does not support workspace-specific configuration. Using global.")
                return self.get_global_config_path(client_name)
        else:
            return self.get_global_config_path(client_name)


