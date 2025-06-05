"""
MCP (Model Context Protocol) - Feedback Module

This module handles user feedback and confirmation for conda actions.
"""
import os
from typing import Dict, Optional

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from .models import ActionPlan

# Initialize console for rich output
console = Console()

class MCPFeedback:
    """
    Manager for user feedback and confirmation.
    
    This class handles presenting action plans to users for confirmation
    and displaying execution results in a user-friendly format.
    """
    
    def __init__(self) -> None:
        """Initialize the feedback manager."""
        pass
    
    def present_action_plan(self, action_plan: ActionPlan) -> bool:
        """
        Present an action plan to the user for confirmation.
        
        Args:
            action_plan: Action plan with details about the proposed action
            
        Returns:
            bool: True if the user confirms, False otherwise
        """
        action_type = action_plan.action
        description = action_plan.description
        
        # Create a rich panel with the action plan details
        panel = Panel(
            self._format_action_details(action_plan),
            title=f"Proposed Action: {action_type.replace('_', ' ').title()}",
            border_style="cyan"
        )
        
        # Display the panel
        console.print("\n")
        console.print(panel)
        console.print("\n")
        
        # Get user confirmation
        return self._get_confirmation()
    
    def display_result(self, result: Dict) -> None:
        """
        Display the result of an action execution.
        
        Args:
            result: Result of the action execution
        """
        success = result.get("success", False)
        message = result.get("message", "")
        
        # Create a rich panel with the result details
        panel = Panel(
            message,
            title="✅ Success" if success else "❌ Error",
            border_style="green" if success else "red"
        )
        
        # Display the panel
        console.print("\n")
        console.print(panel)
        console.print("\n")
    
    def _format_action_details(self, action_plan: ActionPlan) -> str:
        """
        Format the details of an action plan for display.
        
        Args:
            action_plan: Action plan with details about the proposed action
            
        Returns:
            str: Formatted action details
        """
        action_type = action_plan.action
        
        if action_type == "create_environment":
            name = action_plan.name or ""
            python_version = action_plan.python_version or ""
            packages = action_plan.packages or []
            
            return (
                f"I'll create a new conda environment with these specifications:\n\n"
                f"Name: [bold]{name}[/bold]\n"
                f"Python version: [bold]{python_version}[/bold]\n"
                f"Packages: [bold]{', '.join(packages)}[/bold]"
            )
        
        elif action_type == "install_packages":
            environment = action_plan.environment or ""
            packages = action_plan.packages or []
            
            return (
                f"I'll install these packages in the [bold]{environment}[/bold] environment:\n\n"
                f"Packages: [bold]{', '.join(packages)}[/bold]"
            )
        
        elif action_type == "update_packages":
            environment = action_plan.environment or ""
            exclude = action_plan.exclude or []
            
            return (
                f"I'll update all packages in the [bold]{environment}[/bold] environment.\n\n"
                f"The following packages will be preserved at their current versions:\n"
                f"[bold]{', '.join(exclude)}[/bold]"
            )
        
        elif action_type == "remove_environment":
            name = action_plan.name or ""
            
            return (
                f"[bold red]Warning:[/bold red] I'll remove the [bold]{name}[/bold] environment.\n"
                f"This action cannot be undone and all packages in this environment will be deleted."
            )
        
        elif action_type == "clean_cache":
            return "I'll clean the conda cache to free up disk space."
        
        else:
            return action_plan.description or "Unknown action"
    
    def _get_confirmation(self) -> bool:
        """
        Get user confirmation.
        
        Returns:
            bool: True if the user confirms, False otherwise
        """
        while True:
            response = console.input("[bold cyan]Would you like me to proceed? (y/n): [/bold cyan]")
            if response.lower() in ["y", "yes"]:
                return True
            elif response.lower() in ["n", "no"]:
                return False
            else:
                console.print("[yellow]Please enter 'y' or 'n'.[/yellow]")
