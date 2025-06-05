"""
MCP (Model Context Protocol) - Environment Management Module

This module handles the creation and management of conda environments for MCP servers.
"""
import json
import os
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from .models import EnvironmentInfo


class MCPEnvironmentManager:
    """
    Environment Management for MCP servers.
    
    This class handles the creation, tracking, and removal of conda environments
    for MCP servers.
    """
    
    def __init__(self, base_path: Optional[str] = None):
        """
        Initialize the environment manager.
        
        Args:
            base_path: Base path for MCP environments. If None, defaults to ~/.anaconda/mcp
        """
        if base_path is None:
            home = os.path.expanduser("~")
            self.base_path = os.path.join(home, ".anaconda", "mcp")
        else:
            self.base_path = base_path
            
        # Ensure the base directory exists
        os.makedirs(self.base_path, exist_ok=True)
        
        # Path to the environment registry
        self.registry_path = os.path.join(self.base_path, "registry.json")
        
        # Initialize or load the registry
        self._initialize_registry()
    
    def _initialize_registry(self) -> None:
        """Initialize or load the environment registry."""
        if os.path.exists(self.registry_path):
            with open(self.registry_path, "r") as f:
                self.registry = json.load(f)
        else:
            self.registry = {"environments": {}}
            self._save_registry()
    
    def _save_registry(self) -> None:
        """Save the environment registry to disk."""
        with open(self.registry_path, "w") as f:
            json.dump(self.registry, f, indent=2)
    
    def create_environment(self, server_name: str, python_version: str = "3.10") -> str:
        """
        Create a conda environment for an MCP server.
        
        Args:
            server_name: Name of the MCP server
            python_version: Python version to use in the environment
            
        Returns:
            str: Path to the created environment
        """
        # Generate a unique environment name
        env_name = f"mcp-{server_name}-{int(time.time())}"
        env_path = os.path.join(self.base_path, "envs", env_name)
        
        # In a real implementation, this would use the conda API to create the environment
        # For now, we'll just simulate it by creating the directory
        os.makedirs(os.path.join(env_path, "conda-meta"), exist_ok=True)
        
        # Record the environment in the registry
        timestamp = datetime.now().isoformat()
        self.registry["environments"][server_name] = {
            "name": env_name,
            "path": env_path,
            "server_name": server_name,
            "python_version": python_version,
            "created_at": timestamp,
            "last_updated": timestamp
        }
        self._save_registry()
        
        return env_path
    
    def remove_environment(self, server_name: str) -> bool:
        """
        Remove a conda environment for an MCP server.
        
        Args:
            server_name: Name of the MCP server
            
        Returns:
            bool: True if the environment was removed, False otherwise
        """
        if server_name not in self.registry["environments"]:
            return False
        
        env_info = self.registry["environments"][server_name]
        env_path = env_info["path"]
        
        # In a real implementation, this would use the conda API to remove the environment
        # For now, we'll just simulate it
        
        # Remove the environment from the registry
        del self.registry["environments"][server_name]
        self._save_registry()
        
        return True
    
    def get_environment_path(self, server_name: str) -> Optional[str]:
        """
        Get the path to a server's conda environment.
        
        Args:
            server_name: Name of the MCP server
            
        Returns:
            Optional[str]: Path to the environment if found, None otherwise
        """
        if server_name not in self.registry["environments"]:
            return None
        
        return self.registry["environments"][server_name]["path"]
    
    def list_environments(self) -> Dict[str, EnvironmentInfo]:
        """
        List all managed environments and their associated servers.
        
        Returns:
            Dict[str, EnvironmentInfo]: Dictionary mapping server names to environment info
        """
        result = {}
        
        for server_name, env_data in self.registry["environments"].items():
            result[server_name] = EnvironmentInfo(
                name=env_data["name"],
                path=env_data["path"],
                server_name=server_name,
                python_version=env_data["python_version"],
                created_at=env_data["created_at"],
                last_updated=env_data.get("last_updated")
            )
        
        return result
    
    def update_environment(self, server_name: str) -> bool:
        """
        Update the timestamp for an environment.
        
        Args:
            server_name: Name of the MCP server
            
        Returns:
            bool: True if the environment was updated, False otherwise
        """
        if server_name not in self.registry["environments"]:
            return False
        
        self.registry["environments"][server_name]["last_updated"] = datetime.now().isoformat()
        self._save_registry()
        
        return True
