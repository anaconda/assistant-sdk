"""
MCP Service module - Implements the workflow-oriented architecture for MCP Manager.

This module integrates the workflow-oriented architecture with the existing service interface.
"""
from typing import Dict, List, Optional, Any
import os
from enum import Enum

from .models import ClientType, ServerInfo, InstallationResult
from .command_router import CommandRouter
from .execution_context import ExecutionContext

class MCPService:
    """
    MCP Service for managing MCP servers.
    
    This class implements the service layer using the workflow-oriented architecture.
    It maintains the same interface as before but uses the workflow modules internally.
    """
    
    def __init__(self) -> None:
        """Initialize the MCP service."""
        self.router = CommandRouter()
    
    def list_available_servers(self) -> List[ServerInfo]:
        """
        List available MCP servers from the catalog.
        
        Returns:
            List of ServerInfo objects
        """
        # Use the discovery workflow through the command router
        context = ExecutionContext(workflow_name="discovery")
        result = self.router.route_list_command(context)
        
        # Convert the result to ServerInfo objects
        servers = []
        for server_data in result.get("servers", []):
            server = ServerInfo(
                name=server_data.get("name", ""),
                version=server_data.get("version", ""),
                description=server_data.get("description", ""),
                dependencies=server_data.get("dependencies", []),
                homepage=server_data.get("homepage", ""),
                repository=server_data.get("repository", ""),
                author=server_data.get("author", ""),
                license=server_data.get("license", "")
            )
            servers.append(server)
        
        return servers
    
    def get_server_details(self, server_name: str) -> Optional[ServerInfo]:
        """
        Get details about a specific server.
        
        Args:
            server_name: Name of the server
            
        Returns:
            ServerInfo object or None if not found
        """
        # Use the info workflow through the command router
        context = ExecutionContext(workflow_name="info")
        context.server_name = server_name
        result = self.router.route_info_command(context)
        
        if not result.get("success"):
            return None
        
        server_data = result.get("server_info", {})
        if not server_data:
            return None
        
        # Convert the result to a ServerInfo object
        return ServerInfo(
            name=server_data.get("name", ""),
            version=server_data.get("version", ""),
            description=server_data.get("description", ""),
            dependencies=server_data.get("dependencies", []),
            homepage=server_data.get("homepage", ""),
            repository=server_data.get("repository", ""),
            author=server_data.get("author", ""),
            license=server_data.get("license", "")
        )
    
    def install_server(
        self,
        server_name: str,
        client_type: ClientType,
        workspace_path: Optional[str] = None,
        python_version: str = "3.10"
    ) -> InstallationResult:
        """
        Install a server.
        
        Args:
            server_name: Name of the server
            client_type: Type of client
            workspace_path: Path to workspace for workspace-specific config
            python_version: Python version to use in the environment
            
        Returns:
            InstallationResult object
        """
        # Use the install workflow through the command router
        context = ExecutionContext(workflow_name="install")
        context.server_name = server_name
        context.client_name = client_type.value
        context.workspace_path = workspace_path
        context.set_state("python_version", python_version)
        
        result = self.router.route_install_command(context)
        
        # Convert the result to an InstallationResult object
        if result.get("success"):
            # Corrected block for install_server success case
            return InstallationResult(
                success=True,
                server_name=server_name,
                environment_path=result.get("env_path"), # Use default None
                config_path=result.get("config_path"), # Use default None
                error_message=None # Add missing optional field
            )
        else:
            return InstallationResult(
                success=False,
                server_name=server_name,
                error_message=result.get("error", "Unknown error"),
                environment_path=None, # Use None for failure case
                config_path=None # Use None for failure case
            )
    
    def update_server(
        self,
        server_name: str,
        client_type: ClientType,
        workspace_path: Optional[str] = None
    ) -> InstallationResult:
        """
        Update an installed server.
        
        Args:
            server_name: Name of the server
            client_type: Type of client
            workspace_path: Path to workspace for workspace-specific config
            
        Returns:
            InstallationResult object
        """
        # Use the update workflow through the command router
        context = ExecutionContext(workflow_name="update")
        context.server_name = server_name
        context.client_name = client_type.value
        context.workspace_path = workspace_path
        
        result = self.router.route_update_command(context)
        
        # Convert the result to an InstallationResult object
        if result.get("success"):
            # Corrected block for update_server success case
            return InstallationResult(
                success=True,
                server_name=server_name,
                environment_path=result.get("env_path"), # Use default None
                config_path=result.get("config_path"), # Use default None
                error_message=None # Add missing optional field
            )
        else:
            return InstallationResult(
                success=False,
                server_name=server_name,
                error_message=result.get("error", "Unknown error"),
                environment_path=None, # Use None for failure case
                config_path=None # Use None for failure case
            )
    
    def uninstall_server(
        self,
        server_name: str,
        client_type: ClientType,
        workspace_path: Optional[str] = None
    ) -> bool:
        """
        Uninstall a server.
        
        Args:
            server_name: Name of the server
            client_type: Type of client
            workspace_path: Path to workspace for workspace-specific config
            
        Returns:
            True if successful, False otherwise
        """
        # Use the uninstall workflow through the command router
        context = ExecutionContext(workflow_name="uninstall")
        context.server_name = server_name
        context.client_name = client_type.value
        context.workspace_path = workspace_path
        
        result = self.router.route_uninstall_command(context)
        
        return result.get("success", False)
    
    def list_installed_servers(
        self,
        client_type: Optional[ClientType] = None,
        workspace_path: Optional[str] = None
    ) -> Dict[str, List[Any]]:
        """
        List installed servers.
        
        Args:
            client_type: Type of client to filter by
            workspace_path: Path to workspace to filter by
            
        Returns:
            Dict mapping client names to lists of server objects
        """
        # Use the management workflow through the command router
        context = ExecutionContext(workflow_name="management")
        if client_type:
            context.client_name = client_type.value
        context.workspace_path = workspace_path
        
        result = self.router.route_status_command(context)
        
        # Convert the result to the expected format
        installed_servers: Dict[str, List[Any]] = {}
        
        if result.get("success"):
            servers = result.get("servers", [])
            
            # Group servers by client
            for server in servers:
                client_name = server.get("client_name", "unknown")
                
                if client_name not in installed_servers:
                    installed_servers[client_name] = []
                
                # Create a server object with the expected attributes
                server_obj = type("ServerObject", (), {
                    "name": server.get("name", ""),
                    "environment_path": server.get("env_path", ""),
                    "command": server.get("command", ""),
                    "workspace_path": server.get("workspace_path", None)
                })
                
                installed_servers[client_name].append(server_obj)
        
        return installed_servers
