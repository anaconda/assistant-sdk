"""
Command Router module for MCP Manager.

This module routes commands to the appropriate workflow modules.
"""
from typing import List, Optional, Dict, Any
import typer
from enum import Enum

from .execution_context import ExecutionContext, WorkflowPhase
from .workflows.install_flow import InstallFlow
from .workflows.discovery_flow import DiscoveryFlow
from .workflows.management_flow import ManagementFlow
from .workflows.update_flow import UpdateFlow
from .workflows.info_flow import InfoFlow
from .workflows.uninstall_flow import UninstallFlow

class CommandRouter:
    """
    Command Router for MCP Manager.
    
    Routes commands to the appropriate workflow modules and manages
    the execution context throughout the workflow.
    """
    
    def __init__(self) -> None:
        """Initialize the command router."""
        self.install_flow = InstallFlow()
        self.discovery_flow = DiscoveryFlow()
        self.management_flow = ManagementFlow()
        self.update_flow = UpdateFlow()
        self.info_flow = InfoFlow()
        self.uninstall_flow = UninstallFlow()
    
    def route_list_command(self, context: ExecutionContext) -> Dict[str, Any]:
        """
        Route the list command to the discovery flow.
        
        Args:
            context: Execution context for the workflow
            
        Returns:
            Dict with the command result
        """
        context.set_phase(WorkflowPhase.DISCOVERY)
        
        return self.discovery_flow.list_available_servers(context)
    
    def route_info_command(self, context: ExecutionContext) -> Dict[str, Any]:
        """
        Route the info command to the info flow.
        
        Args:
            context: Execution context for the workflow
            
        Returns:
            Dict with the command result
        """
        context.set_phase(WorkflowPhase.DISCOVERY)
        
        return self.info_flow.get_server_info(context)
    
    def route_install_command(self, context: ExecutionContext) -> Dict[str, Any]:
        """
        Route the install command to the install flow.
        
        Args:
            context: Execution context for the workflow
            
        Returns:
            Dict with the command result
        """
        context.set_phase(WorkflowPhase.INIT)
        
        return self.install_flow.install_server(context)
    
    def route_update_command(self, context: ExecutionContext) -> Dict[str, Any]:
        """
        Route the update command to the update flow.
        
        Args:
            context: Execution context for the workflow
            
        Returns:
            Dict with the command result
        """
        context.set_phase(WorkflowPhase.INIT)
        
        return self.update_flow.update_server(context)
    
    def route_uninstall_command(self, context: ExecutionContext) -> Dict[str, Any]:
        """
        Route the uninstall command to the uninstall flow.
        
        Args:
            context: Execution context for the workflow
            
        Returns:
            Dict with the command result
        """
        context.set_phase(WorkflowPhase.INIT)
        
        return self.uninstall_flow.uninstall_server(context)
    
    def route_status_command(self, context: ExecutionContext) -> Dict[str, Any]:
        """
        Route the status command to the management flow.
        
        Args:
            context: Execution context for the workflow
            
        Returns:
            Dict with the command result
        """
        context.set_phase(WorkflowPhase.DISCOVERY)
        
        return self.management_flow.list_installed_servers(context)
