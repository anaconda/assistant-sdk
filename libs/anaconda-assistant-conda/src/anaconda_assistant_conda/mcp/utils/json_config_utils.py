"""
JSON Configuration Utilities module for MCP Manager.

This module provides utilities for working with JSON configuration files.
"""
from typing import Dict, Any, Optional, List
import os
import json

class JsonConfigUtils:
    """
    JSON Configuration Utilities for MCP Manager.
    
    Provides utilities for working with JSON configuration files.
    """
    
    def __init__(self) -> None:
        """Initialize the JSON configuration utilities."""
        pass
    
    def load_config(self, config_path: str) -> Dict[str, Any]:
        """
        Load configuration from a JSON file.
        
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
    
    def save_config(self, config_path: str, config: Dict[str, Any]) -> bool:
        """
        Save configuration to a JSON file.
        
        Args:
            config_path: Path to the configuration file
            config: Configuration to save
            
        Returns:
            True if save succeeded, False otherwise
        """
        # Create parent directory if it doesn't exist
        os.makedirs(os.path.dirname(config_path), exist_ok=True)
        
        try:
            # Save the configuration
            with open(config_path, "w") as f:
                json.dump(config, f, indent=2)
            return True
        except Exception:
            return False
    
    def add_server_to_config(
        self,
        config_path: str,
        server_name: str,
        env_path: str,
        command: str,
        workspace_path: Optional[str] = None
    ) -> bool:
        """
        Add a server to a configuration file.
        
        Args:
            config_path: Path to the configuration file
            server_name: Name of the server
            env_path: Path to the conda environment
            command: Command to start the server
            workspace_path: Path to workspace for workspace-specific config
            
        Returns:
            True if addition succeeded, False otherwise
        """
        # Load the configuration
        config = self.load_config(config_path)
        
        # Ensure servers list exists
        if "servers" not in config:
            config["servers"] = []
        
        # Check if server already exists
        for i, server in enumerate(config["servers"]):
            if server.get("name") == server_name:
                # Update existing server
                config["servers"][i] = {
                    "name": server_name,
                    "environment_path": env_path,
                    "command": command,
                    "workspace_path": workspace_path
                }
                return self.save_config(config_path, config)
        
        # Add new server
        config["servers"].append({
            "name": server_name,
            "environment_path": env_path,
            "command": command,
            "workspace_path": workspace_path
        })
        
        return self.save_config(config_path, config)
    
    def remove_server_from_config(
        self,
        config_path: str,
        server_name: str
    ) -> bool:
        """
        Remove a server from a configuration file.
        
        Args:
            config_path: Path to the configuration file
            server_name: Name of the server
            
        Returns:
            True if removal succeeded, False otherwise
        """
        # Load the configuration
        config = self.load_config(config_path)
        
        # Ensure servers list exists
        if "servers" not in config:
            return True
        
        # Remove server from list
        config["servers"] = [s for s in config["servers"] if s.get("name") != server_name]
        
        return self.save_config(config_path, config)
    
    def list_servers_in_config(self, config_path: str) -> List[Dict[str, Any]]:
        """
        List servers in a configuration file.
        
        Args:
            config_path: Path to the configuration file
            
        Returns:
            List of server information dictionaries
        """
        # Load the configuration
        config = self.load_config(config_path)
        
        # Ensure servers list exists
        if "servers" not in config:
            return []
        
        return config["servers"]
