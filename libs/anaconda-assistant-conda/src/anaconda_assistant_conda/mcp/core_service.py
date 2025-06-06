"""
Core Service module for MCP Manager.

This module acts as a facade for the individual service modules.
"""
from typing import Dict, Any, Optional, List
import os
import json

from .services.catalog import CatalogService
from .services.environment import EnvironmentService
from .services.installation import InstallationService
from .services.configuration import ConfigurationService

class CoreService:
    """
    Core Service for MCP Manager.
    
    Acts as a facade for the individual service modules, providing
    a unified interface for workflows to interact with services.
    """
    
    def __init__(self) -> None:
        """Initialize the core service."""
        self.catalog_service = CatalogService()
        self.environment_service = EnvironmentService()
        self.installation_service = InstallationService()
        self.configuration_service = ConfigurationService()
    
    def get_server_info(self, server_name: str) -> Optional[Dict[str, Any]]:
        """
        Get information about a server from the catalog.
        
        Args:
            server_name: Name of the server
            
        Returns:
            Dict with server information or None if not found
        """
        return self.catalog_service.get_server_info(server_name)
    
    def list_available_servers(self) -> List[Dict[str, Any]]:
        """
        List available servers from the catalog.
        
        Returns:
            List of server information dictionaries
        """
        return self.catalog_service.list_available_servers()
    
    def create_environment(
        self, 
        server_name: str, 
        python_version: Optional[str] = None
    ) -> Optional[str]:
        """
        Create a conda environment for a server.
        
        Args:
            server_name: Name of the server
            python_version: Python version to use in the environment
            
        Returns:
            Path to the created environment or None if creation failed
        """
        return self.environment_service.create_environment(server_name, python_version)
    
    def install_package(self, server_name: str, env_path: str) -> bool:
        """
        Install a server package in a conda environment.
        
        Args:
            server_name: Name of the server
            env_path: Path to the conda environment
            
        Returns:
            True if installation succeeded, False otherwise
        """
        return self.installation_service.install_package(server_name, env_path)
    
    def update_package(self, server_name: str, env_path: str) -> bool:
        """
        Update a server package in a conda environment.
        
        Args:
            server_name: Name of the server
            env_path: Path to the conda environment
            
        Returns:
            True if update succeeded, False otherwise
        """
        return self.installation_service.update_package(server_name, env_path)
    
    def generate_server_command(self, server_name: str, env_path: str) -> str:
        """
        Generate the command to start a server.
        
        Args:
            server_name: Name of the server
            env_path: Path to the conda environment
            
        Returns:
            Command to start the server
        """
        return self.installation_service.generate_server_command(server_name, env_path)
    
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
        return self.configuration_service.update_client_configuration(
            server_name, client_name, env_path, command, workspace_path
        )
    
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
        return self.configuration_service.remove_server_from_configuration(
            server_name, client_name, workspace_path
        )
    
    def remove_environment(self, server_name: str) -> bool:
        """
        Remove a conda environment for a server.
        
        Args:
            server_name: Name of the server
            
        Returns:
            True if removal succeeded, False otherwise
        """
        return self.environment_service.remove_environment(server_name)
    
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
        return self.configuration_service.list_installed_servers(client_name, workspace_path)
    
    def verify_installation(self, server_name: str) -> bool:
        """
        Verify that a server is correctly installed and operational.
        
        Args:
            server_name: Name of the server
            
        Returns:
            True if the server is correctly installed, False otherwise
        """
        env_path = self.environment_service.get_environment_path(server_name)
        if not env_path:
            return False
        
        return self.installation_service.verify_installation(server_name, env_path)
