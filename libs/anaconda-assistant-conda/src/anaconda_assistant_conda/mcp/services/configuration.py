"""
Configuration Service module for MCP Manager.

This module handles client configuration management.
"""
from typing import Dict, Any, Optional, List
import os
import json

class ConfigurationService:
    """
    Configuration Service for MCP Manager.
    
    Handles client configuration management for MCP servers.
    """
    
    def __init__(self) -> None:
        """Initialize the configuration service."""
        # In a real implementation, this would interact with config files
        self.configurations: Dict[str, List[Dict[str, Any]]] = {
            "claude-desktop": [],
            "cursor": [],
            "vscode": [],
            "custom": []
        }
    
    def update_client_configuration(
        self,
        server_name: str,
        client_name: str,
        env_path: str,
        command: str,
        workspace_path: Optional[str] = None
    ) -> bool:
        """
        Update client configuration with server information.
        
        Args:
            server_name: Name of the server
            client_name: Name of the client
            env_path: Path to the conda environment
            command: Command to start the server
            workspace_path: Path to workspace for workspace-specific config
            
        Returns:
            True if configuration update succeeded, False otherwise
        """
        if client_name not in self.configurations:
            return False
        
        # Remove existing configuration for this server if it exists
        self.configurations[client_name] = [
            s for s in self.configurations[client_name] 
            if s.get("name") != server_name or s.get("workspace_path") != workspace_path
        ]
        
        # Add new configuration
        self.configurations[client_name].append({
            "name": server_name,
            "env_path": env_path,
            "command": command,
            "workspace_path": workspace_path,
            "is_active": True
        })
        
        return True
    
    def remove_server_from_configuration(
        self,
        server_name: str,
        client_name: str,
        workspace_path: Optional[str] = None
    ) -> bool:
        """
        Remove a server from client configuration.
        
        Args:
            server_name: Name of the server
            client_name: Name of the client
            workspace_path: Path to workspace for workspace-specific config
            
        Returns:
            True if removal succeeded, False otherwise
        """
        if client_name not in self.configurations:
            return False
        
        initial_count = len(self.configurations[client_name])
        
        # Remove configuration for this server
        self.configurations[client_name] = [
            s for s in self.configurations[client_name] 
            if s.get("name") != server_name or s.get("workspace_path") != workspace_path
        ]
        
        # Return True if something was removed
        return len(self.configurations[client_name]) < initial_count
    
    def list_installed_servers(
        self,
        client_name: Optional[str] = None,
        workspace_path: Optional[str] = None
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        List installed servers, optionally filtered by client and workspace.
        
        Args:
            client_name: Name of the client to filter by
            workspace_path: Path to workspace to filter by
            
        Returns:
            Dict mapping client names to lists of server information
        """
        result = {}
        
        # Filter by client if specified
        clients_to_check = [client_name] if client_name else self.configurations.keys()
        
        for client in clients_to_check:
            if client not in self.configurations:
                continue
            
            # Filter by workspace if specified
            if workspace_path:
                servers = [
                    s for s in self.configurations[client]
                    if s.get("workspace_path") == workspace_path
                ]
            else:
                servers = self.configurations[client]
            
            if servers:
                result[client] = servers
        
        return result
