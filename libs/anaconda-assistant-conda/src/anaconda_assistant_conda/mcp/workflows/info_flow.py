"""
Info Flow module for MCP Manager.

This module implements the workflow for retrieving information about MCP servers.
"""
from typing import Dict, Any, Optional

from ..execution_context import ExecutionContext, WorkflowPhase
from ..core_service import CoreService

class InfoFlow:
    """
    Info Flow for MCP Manager.
    
    Implements the workflow for retrieving information about MCP servers.
    """
    
    def __init__(self) -> None:
        """Initialize the info flow."""
        self.core_service = CoreService()
    
    def get_server_info(self, context: ExecutionContext) -> Dict[str, Any]:
        """
        Execute the server info workflow.
        
        Args:
            context: Execution context for the workflow
            
        Returns:
            Dict with the server information
        """
        # --- Pre-checks ---
        if context.server_name is None:
            context.set_error("Server name is required for info workflow.")
            return context.get_result_summary()
        
        # Ensure mypy knows server_name is now str
        server_name: str = context.server_name
        
        # Start the workflow
        context.add_to_history("workflow_start", {
            "server_name": server_name
        })
        
        # Start discovery phase
        try:
            context.set_phase(WorkflowPhase.DISCOVERY)
            
            # Get server info from catalog
            server_info = self.core_service.get_server_info(server_name)
            
            if not server_info:
                context.set_error(f"Server {server_name} not found in catalog")
                return context.get_result_summary()
            
            context.set_state("server_info", server_info)
        except Exception as e:
            context.set_error(f"Failed during discovery phase: {str(e)}")
            return context.get_result_summary()
        
        # Complete workflow
        context.set_phase(WorkflowPhase.COMPLETION)
        context.add_to_history("workflow_complete", {
            "server_name": server_name
        })
        
        return context.get_result_summary()