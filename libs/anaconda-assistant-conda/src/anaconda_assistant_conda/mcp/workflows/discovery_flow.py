"""
Discovery Flow module for MCP Manager.

This module implements the workflow for discovering available MCP servers.
"""
from typing import Dict, Any, List

from ..execution_context import ExecutionContext, WorkflowPhase
from ..core_service import CoreService

class DiscoveryFlow:
    """
    Discovery Flow for MCP Manager.
    
    Implements the workflow for discovering available MCP servers.
    """
    
    def __init__(self) -> None:
        """Initialize the discovery flow."""
        self.core_service = CoreService()
    
    def list_available_servers(self, context: ExecutionContext) -> Dict[str, Any]:
        """
        Execute the server discovery workflow.
        
        Args:
            context: Execution context for the workflow
            
        Returns:
            Dict with the discovery result
        """
        # Start the workflow
        context.add_to_history("workflow_start", {
            "action": "list_available_servers"
        })
        
        # Start discovery phase
        try:
            context.set_phase(WorkflowPhase.DISCOVERY)
            
            # Get available servers from catalog
            servers = self.core_service.list_available_servers()
            
            context.set_state("available_servers", servers)
        except Exception as e:
            context.set_error(f"Failed during discovery phase: {str(e)}")
            return context.get_result_summary()
        
        # Complete workflow
        context.set_phase(WorkflowPhase.COMPLETION)
        context.add_to_history("workflow_complete", {
            "server_count": len(context.get_state("available_servers", []))
        })
        
        return context.get_result_summary()
