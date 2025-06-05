"""
MCP (Model Context Protocol) - Configuration Module

This module handles the configuration of MCP clients to use MCP servers.
"""
import json
import os
from pathlib import Path
from typing import Dict, List, Optional

from .models import ClientType, ConfiguredServerInfo


class MCPConfigurator:
    """
    Configuration manager for MCP clients.
    
    This class handles the configuration of MCP clients to use MCP servers,
    including editing JSON configuration files.
    """
    
    def __init__(self) -> None:
        """Initialize the configurator with client-specific config paths."""
        # Default config file locations for different client types
        home = os.path.expanduser("~")
        self.client_config_paths = {
            ClientType.CLAUDE_DESKTOP: os.path.join(
                home, "Library", "Application Support", "Claude", "claude_desktop_config.json"
            ),
            ClientType.CURSOR: os.path.join(
                home, ".cursor", "mcp_config.json"
            ),
            ClientType.VSCODE: os.path.join(
                home, ".vscode", "mcp_config.json"
            ),
            # Custom client type will require explicit path
        }
        
        # Ensure parent directories exist for default config paths
        for path in self.client_config_paths.values():
            os.makedirs(os.path.dirname(path), exist_ok=True)
    
    def _get_config_path(self, client_type: ClientType, workspace_path: Optional[str] = None) -> str:
        """
        Get the path to the configuration file for a client.
        
        Args:
            client_type: Type of MCP client
            workspace_path: Path to workspace for workspace-specific config
            
        Returns:
            str: Path to the configuration file
            
        Raises:
            ValueError: If client_type is CUSTOM and workspace_path is None
        """
        if workspace_path:
            # Workspace-specific config
            return os.path.join(workspace_path, ".mcp", "config.json")
        
        if client_type == ClientType.CUSTOM:
            raise ValueError("Workspace path is required for custom client type")
        
        return self.client_config_paths[client_type]
    
    def _load_config(self, config_path: str) -> Dict:
        """
        Load a configuration file.
        
        Args:
            config_path: Path to the configuration file
            
        Returns:
            Dict: Configuration data
        """
        if os.path.exists(config_path):
            with open(config_path, "r") as f:
                return json.load(f)
        
        # Initialize with empty config
        return {"mcpServers": []}
    
    def _save_config(self, config_path: str, config_data: Dict) -> None:
        """
        Save a configuration file.
        
        Args:
            config_path: Path to the configuration file
            config_data: Configuration data to save
        """
        # Ensure the directory exists
        os.makedirs(os.path.dirname(config_path), exist_ok=True)
        
        with open(config_path, "w") as f:
            json.dump(config_data, f, indent=2)
    
    def add_server_to_config(
        self, 
        server_name: str, 
        client_type: ClientType, 
        env_path: str, 
        command: str,
        workspace_path: Optional[str] = None
    ) -> bool:
        """
        Add a server entry to a client's configuration file.
        
        Args:
            server_name: Name of the MCP server
            client_type: Type of MCP client
            env_path: Path to the conda environment
            command: Command to start the server
            workspace_path: Path to workspace for workspace-specific config
            
        Returns:
            bool: True if the server was added, False otherwise
        """
        try:
            config_path = self._get_config_path(client_type, workspace_path)
            config_data = self._load_config(config_path)
            
            # Check if the server is already in the config
            for server in config_data["mcpServers"]:
                if server["name"] == server_name:
                    # Update existing server
                    server["command"] = command
                    server["directory"] = env_path
                    self._save_config(config_path, config_data)
                    return True
            
            # Add new server
            config_data["mcpServers"].append({
                "name": server_name,
                "command": command,
                "directory": env_path
            })
            
            self._save_config(config_path, config_data)
            return True
            
        except Exception as e:
            print(f"Error adding server to config: {e}")
            return False
    
    def remove_server_from_config(
        self, 
        server_name: str, 
        client_type: ClientType, 
        workspace_path: Optional[str] = None
    ) -> bool:
        """
        Remove a server entry from a client's configuration file.
        
        Args:
            server_name: Name of the MCP server
            client_type: Type of MCP client
            workspace_path: Path to workspace for workspace-specific config
            
        Returns:
            bool: True if the server was removed, False otherwise
        """
        try:
            config_path = self._get_config_path(client_type, workspace_path)
            
            if not os.path.exists(config_path):
                return False
            
            config_data = self._load_config(config_path)
            
            # Filter out the server
            original_count = len(config_data["mcpServers"])
            config_data["mcpServers"] = [
                server for server in config_data["mcpServers"] 
                if server["name"] != server_name
            ]
            
            # Check if any server was removed
            if len(config_data["mcpServers"]) == original_count:
                return False
            
            self._save_config(config_path, config_data)
            return True
            
        except Exception as e:
            print(f"Error removing server from config: {e}")
            return False
    
    def list_configured_servers(
        self, 
        client_type: ClientType, 
        workspace_path: Optional[str] = None
    ) -> List[ConfiguredServerInfo]:
        """
        List all servers configured for a specific client.
        
        Args:
            client_type: Type of MCP client
            workspace_path: Path to workspace for workspace-specific config
            
        Returns:
            List[ConfiguredServerInfo]: List of configured servers
        """
        try:
            config_path = self._get_config_path(client_type, workspace_path)
            
            if not os.path.exists(config_path):
                return []
            
            config_data = self._load_config(config_path)
            
            result = []
            for server in config_data.get("mcpServers", []):
                result.append(ConfiguredServerInfo(
                    name=server["name"],
                    environment_path=server["directory"],
                    client=client_type,
                    workspace_path=workspace_path,
                    command=server["command"],
                    is_active=True  # Assume all configured servers are active
                ))
            
            return result
            
        except Exception as e:
            print(f"Error listing configured servers: {e}")
            return []
