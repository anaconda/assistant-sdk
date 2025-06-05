"""
Execution Context module for MCP Manager.

This module implements the execution context pattern for workflow state management.
"""
from typing import Dict, Any, Optional, List
from enum import Enum, auto
from dataclasses import dataclass, field

class WorkflowPhase(Enum):
    """Phases of a workflow execution."""
    INIT = auto()
    DISCOVERY = auto()
    ENVIRONMENT = auto()
    INSTALLATION = auto()
    CONFIGURATION = auto()
    COMPLETION = auto()
    ERROR = auto()

@dataclass
class ExecutionContext:
    """
    Execution context for workflow state management.
    
    The execution context maintains state throughout a workflow execution,
    tracking progress, decisions, and results across multiple steps.
    """
    # Basic workflow information
    workflow_name: str
    server_name: Optional[str] = None
    client_name: Optional[str] = None
    workspace_path: Optional[str] = None
    
    # Current phase of execution
    current_phase: WorkflowPhase = WorkflowPhase.INIT
    
    # Error tracking
    error_message: Optional[str] = None
    has_error: bool = False
    
    # State storage
    state: Dict[str, Any] = field(default_factory=dict)
    
    # History of actions and decisions
    history: List[Dict[str, Any]] = field(default_factory=list)
    
    def set_phase(self, phase: WorkflowPhase) -> None:
        """
        Update the current phase of the workflow.
        
        Args:
            phase: The new phase
        """
        self.current_phase = phase
        self.add_to_history("phase_change", {"new_phase": phase.name})
    
    def set_error(self, message: str) -> None:
        """
        Set an error in the context.
        
        Args:
            message: Error message
        """
        self.has_error = True
        self.error_message = message
        self.current_phase = WorkflowPhase.ERROR
        self.add_to_history("error", {"message": message})
    
    def add_to_history(self, action: str, details: Dict[str, Any]) -> None:
        """
        Add an action to the history.
        
        Args:
            action: Name of the action
            details: Details of the action
        """
        entry = {
            "action": action,
            "phase": self.current_phase.name,
            "details": details
        }
        self.history.append(entry)
    
    def set_state(self, key: str, value: Any) -> None:
        """
        Set a value in the state dictionary.
        
        Args:
            key: State key
            value: State value
        """
        self.state[key] = value
        self.add_to_history("state_change", {"key": key, "value": str(value)})
    
    def get_state(self, key: str, default: Any = None) -> Any:
        """
        Get a value from the state dictionary.
        
        Args:
            key: State key
            default: Default value if key doesn't exist
            
        Returns:
            The value or default
        """
        return self.state.get(key, default)
    
    def is_complete(self) -> bool:
        """
        Check if the workflow is complete.
        
        Returns:
            True if the workflow is in the COMPLETION phase
        """
        return self.current_phase == WorkflowPhase.COMPLETION
    
    def has_failed(self) -> bool:
        """
        Check if the workflow has failed.
        
        Returns:
            True if the workflow is in the ERROR phase
        """
        return self.current_phase == WorkflowPhase.ERROR
    
    def get_result_summary(self) -> Dict[str, Any]:
        """
        Get a summary of the workflow execution.
        
        Returns:
            Dictionary with workflow results
        """
        return {
            "workflow": self.workflow_name,
            "server": self.server_name,
            "client": self.client_name,
            "workspace": self.workspace_path,
            "success": self.is_complete(),
            "error": self.error_message if self.has_failed() else None,
            "state": self.state
        }
