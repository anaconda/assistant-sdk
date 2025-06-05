"""
Management Flow module for MCP Manager.

This module implements the workflow for managing installed MCP servers.
"""
from typing import Dict, Any, Optional, List

from ..execution_context import ExecutionContext, WorkflowPhase
from ..core_service import CoreService

class ManagementFlow:
    """
    Management Flow for MCP Manager.
    
    Implements the workflow for managing installed MCP servers.
    """
    
    def __init__(self) -> None:
        """Initialize the management flow."""
        self.core_service = CoreService()
    
    def list_installed_servers(self, context: ExecutionContext) -> Dict[str, Any]:
        """
        Execute the workflow to list installed servers.
        
        Args:
            context: Execution context for the workflow
            
        Returns:
            Dict with the management result
        """
        # Start the workflow
        context.add_to_history("workflow_start", {
            "action": "list_installed_servers",
            "client_name": context.client_name,
            "workspace_path": context.workspace_path
        })
        
        # Start discovery phase
        try:
            context.set_phase(WorkflowPhase.DISCOVERY)
            
            # Get installed servers
            installed_servers = self.core_service.list_installed_servers(
                context.client_name, context.workspace_path
            )
            
            context.set_state("installed_servers", installed_servers)
        except Exception as e:
            context.set_error(f"Failed during discovery phase: {str(e)}")
            return context.get_result_summary()
        
        # Complete workflow
        context.set_phase(WorkflowPhase.COMPLETION)
        
        # Count total servers across all clients
        total_servers = 0
        for client, servers in context.get_state("installed_servers", {}).items():
            total_servers += len(servers)
            
        context.add_to_history("workflow_complete", {
            "client_count": len(context.get_state("installed_servers", {})),
            "server_count": total_servers
        })
        
        return context.get_result_summary()
