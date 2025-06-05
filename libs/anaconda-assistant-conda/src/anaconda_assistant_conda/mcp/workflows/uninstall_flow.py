"""
Uninstall Flow module for MCP Manager.

This module implements the workflow for uninstalling MCP servers.
"""
from typing import Dict, Any, Optional

from ..execution_context import ExecutionContext, WorkflowPhase
from ..config_resolver import ConfigResolver
from ..core_service import CoreService

class UninstallFlow:
    """
    Uninstall Flow for MCP Manager.
    
    Implements the workflow for uninstalling MCP servers, including
    configuration removal and environment cleanup.
    """
    
    def __init__(self) -> None:
        """Initialize the uninstall flow."""
        self.config_resolver = ConfigResolver()
        self.core_service = CoreService()
    
    def uninstall_server(self, context: ExecutionContext) -> Dict[str, Any]:
        """
        Execute the server uninstallation workflow.
        
        Args:
            context: Execution context for the workflow
            
        Returns:
            Dict with the uninstallation result
        """
        # Pre-checks
        if context.server_name is None:
            context.set_error("Server name is required for uninstall workflow.")
            return context.get_result_summary()
        if context.client_name is None:
            context.set_error("Client name is required for uninstall workflow.")
            return context.get_result_summary()
        
        # Ensure mypy knows server_name and client_name are now str
        server_name: str = context.server_name
        client_name: str = context.client_name
        
        # Start the workflow
        context.add_to_history("workflow_start", {
            "server_name": server_name,
            "client_name": client_name,
            "workspace_path": context.workspace_path
        })
        
        # Resolve client configuration
        try:
            context.set_phase(WorkflowPhase.DISCOVERY)
            client_config = self.config_resolver.resolve_client_config(
                client_name, context.workspace_path
            )
            context.set_state("client_config", client_config)
        except Exception as e:
            context.set_error(f"Failed to resolve client configuration: {str(e)}")
            return context.get_result_summary()
        
        # Start discovery phase
        try:
            # Check if server is installed
            installed_servers = self.core_service.list_installed_servers(
                client_name, context.workspace_path
            )
            
            server_found = False
            
            if client_name in installed_servers:
                for server in installed_servers[client_name]:
                    if server.get("name") == server_name:
                        server_found = True
                        break
            
            if not server_found:
                context.set_error(f"Server '{server_name}' not installed for client '{client_name}'")
                return context.get_result_summary()
        except Exception as e:
            context.set_error(f"Failed during discovery phase: {str(e)}")
            return context.get_result_summary()
        
        # Start configuration phase
        try:
            context.set_phase(WorkflowPhase.CONFIGURATION)
            
            # Remove server from client configuration
            config_success = self.core_service.remove_server_from_configuration(
                server_name,
                client_name,
                context.workspace_path
            )
            
            if not config_success:
                context.set_error("Failed to remove server from client configuration")
                return context.get_result_summary()
            
            # Get the config path for reporting
            config_path = self.config_resolver.get_config_path(
                client_name, context.workspace_path
            )
            context.set_state("config_path", config_path)
        except Exception as e:
            context.set_error(f"Failed during configuration phase: {str(e)}")
            return context.get_result_summary()
        
        # Start environment phase
        try:
            context.set_phase(WorkflowPhase.ENVIRONMENT)
            
            # Remove environment
            env_success = self.core_service.remove_environment(server_name)
            
            if not env_success:
                context.set_error("Failed to remove server environment")
                return context.get_result_summary()
        except Exception as e:
            context.set_error(f"Failed during environment phase: {str(e)}")
            return context.get_result_summary()
        
        # Complete workflow
        context.set_phase(WorkflowPhase.COMPLETION)
        context.add_to_history("workflow_complete", {
            "config_path": context.get_state("config_path")
        })
        
        return context.get_result_summary()
