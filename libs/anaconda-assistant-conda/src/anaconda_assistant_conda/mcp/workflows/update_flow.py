"""
Update Flow module for MCP Manager.

This module implements the workflow for updating MCP servers.
"""
from typing import Dict, Any, Optional

from ..execution_context import ExecutionContext, WorkflowPhase
from ..config_resolver import ConfigResolver
from ..core_service import CoreService

class UpdateFlow:
    """
    Update Flow for MCP Manager.
    
    Implements the workflow for updating MCP servers, including
    package updates and configuration updates.
    """
    
    def __init__(self) -> None:
        """Initialize the update flow."""
        self.config_resolver = ConfigResolver()
        self.core_service = CoreService()
    
    def update_server(self, context: ExecutionContext) -> Dict[str, Any]:
        """
        Execute the server update workflow.
        
        Args:
            context: Execution context for the workflow
            
        Returns:
            Dict with the update result
        """
        # --- Pre-checks ---
        if context.server_name is None:
            context.set_error("Server name is required for update workflow.")
            return context.get_result_summary()
        if context.client_name is None:
            context.set_error("Client name is required for update workflow.")
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
            # Check if server exists in catalog
            server_info = self.core_service.get_server_info(server_name)
            if not server_info:
                context.set_error(f"Server {server_name} not found in catalog")
                return context.get_result_summary()
            
            context.set_state("server_info", server_info)
            
            # Get environment path
            installed_servers = self.core_service.list_installed_servers(
                client_name, context.workspace_path
            )
            
            # Check if server is installed
            server_found = False
            env_path: Optional[str] = None # Initialize env_path
            
            if client_name in installed_servers:
                for server in installed_servers[client_name]:
                    if server.get("name") == server_name:
                        server_found = True
                        env_path = server.get("environment_path")
                        break
            
            if not server_found or not env_path:
                context.set_error(f"Server {server_name} not installed for client {client_name}")
                return context.get_result_summary()
            
            context.set_state("environment_path", env_path)
        except Exception as e:
            context.set_error(f"Failed during discovery phase: {str(e)}")
            return context.get_result_summary()
        
        # Start environment phase
        try:
            context.set_phase(WorkflowPhase.ENVIRONMENT)
            
            # Get env_path again, ensuring it's str
            current_env_path = context.get_state("environment_path")
            if not isinstance(current_env_path, str):
                 context.set_error("Internal error: Environment path not found or invalid.")
                 return context.get_result_summary()

            # Update package in environment
            update_success = self.core_service.update_package(
                server_name, 
                current_env_path
            )
            
            if not update_success:
                context.set_error("Failed to update server package")
                return context.get_result_summary()
        except Exception as e:
            context.set_error(f"Failed during environment phase: {str(e)}")
            return context.get_result_summary()
        
        # Start configuration phase
        try:
            context.set_phase(WorkflowPhase.CONFIGURATION)
            
            # Get env_path again, ensuring it's str
            current_env_path = context.get_state("environment_path")
            if not isinstance(current_env_path, str):
                 context.set_error("Internal error: Environment path not found or invalid after update.")
                 return context.get_result_summary()

            # Generate server command
            command = self.core_service.generate_server_command(
                server_name,
                current_env_path
            )
            
            context.set_state("server_command", command)
            
            # Update client configuration
            config_success = self.core_service.update_client_configuration(
                server_name,
                client_name,
                current_env_path,
                command,
                context.workspace_path
            )
            
            if not config_success:
                context.set_error("Failed to update client configuration")
                return context.get_result_summary()
            
            # Get the config path for reporting
            config_path = self.config_resolver.get_config_path(
                client_name, context.workspace_path
            )
            context.set_state("config_path", config_path)
        except Exception as e:
            context.set_error(f"Failed during configuration phase: {str(e)}")
            return context.get_result_summary()
        
        # Complete workflow
        context.set_phase(WorkflowPhase.COMPLETION)
        context.add_to_history("workflow_complete", {
            "environment_path": context.get_state("environment_path"),
            "config_path": context.get_state("config_path")
        })
        
        return context.get_result_summary()