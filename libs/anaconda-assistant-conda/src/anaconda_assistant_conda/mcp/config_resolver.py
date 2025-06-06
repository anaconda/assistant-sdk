"""
Config Resolver module for MCP Manager.

This module handles client configuration resolution separate from workflows.
"""
from typing import Dict, Any, Optional
import os
import json
from enum import Enum

class ClientType(Enum):
    """Client types supported by MCP Manager."""
    CLAUDE_DESKTOP = "claude-desktop"
    CURSOR = "cursor"
    VSCODE = "vscode"
    CUSTOM = "custom"

class ConfigResolver:
    """
    Config Resolver for MCP Manager.
    
    Handles client configuration resolution separate from workflows.
    """
    
    def __init__(self) -> None:
        """Initialize the config resolver."""
        # Define default config paths for each client type
        self.client_config_paths = {
            ClientType.CLAUDE_DESKTOP: os.path.expanduser("~/.config/claude-desktop/mcp.json"),
            ClientType.CURSOR: os.path.expanduser("~/.cursor/mcp-servers.json"),
            ClientType.VSCODE: os.path.expanduser("~/.vscode/mcp-config.json"),
            ClientType.CUSTOM: os.path.expanduser("~/.mcp/config.json")
        }
    
    def resolve_client_config(
        self, 
        client_name: str, 
        workspace_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Resolve client configuration based on client name and workspace path.
        
        Args:
            client_name: Name of the client
            workspace_path: Path to workspace for workspace-specific config
            
        Returns:
            Dict with client configuration
        """
        try:
            client_type = ClientType(client_name)
        except ValueError:
            raise ValueError(f"Invalid client type: {client_name}")
        
        # Get the config path
        config_path = self.get_config_path(client_name, workspace_path)
        
        # Load the configuration
        config = self._load_config(config_path)
        
        return {
            "client_type": client_type,
            "config_path": config_path,
            "config": config,
            "workspace_path": workspace_path
        }
    
    def get_config_path(
        self, 
        client_name: str, 
        workspace_path: Optional[str] = None
    ) -> str:
        """
        Get the configuration file path for a client.
        
        Args:
            client_name: Name of the client
            workspace_path: Path to workspace for workspace-specific config
            
        Returns:
            Path to the configuration file
        """
        try:
            client_type = ClientType(client_name)
        except ValueError:
            raise ValueError(f"Invalid client type: {client_name}")
        
        # If workspace path is provided, use workspace-specific config
        if workspace_path:
            if client_type == ClientType.VSCODE:
                # VSCode uses .vscode directory in workspace
                return os.path.join(workspace_path, ".vscode", "mcp-config.json")
            elif client_type == ClientType.CURSOR:
                # Cursor uses .cursor directory in workspace
                return os.path.join(workspace_path, ".cursor", "mcp-servers.json")
            else:
                # Other clients use .mcp directory in workspace
                return os.path.join(workspace_path, ".mcp", "config.json")
        
        # Otherwise use global config
        return self.client_config_paths[client_type]
    
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """
        Load configuration from a file.
        
        Args:
            config_path: Path to the configuration file
            
        Returns:
            Dict with configuration
        """
        # Create parent directory if it doesn't exist
        os.makedirs(os.path.dirname(config_path), exist_ok=True)
        
        # If the file doesn't exist, create an empty config
        if not os.path.exists(config_path):
            with open(config_path, "w") as f:
                json.dump({"servers": []}, f)
        
        # Load the configuration
        with open(config_path, "r") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                # If the file is invalid JSON, return an empty config
                return {"servers": []}
