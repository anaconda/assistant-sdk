"""
MCP (Model Context Protocol) - Core models and data structures
"""
from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class ServerInfo(BaseModel):
    """Information about an MCP server."""
    name: str = Field(..., description="Name of the MCP server")
    version: str = Field(..., description="Version of the MCP server")
    description: str = Field(..., description="Description of the MCP server")
    dependencies: List[str] = Field(default_factory=list, description="Dependencies required by the server")
    homepage: Optional[str] = Field(None, description="Homepage URL for the server")
    repository: Optional[str] = Field(None, description="Repository URL for the server")
    author: Optional[str] = Field(None, description="Author of the server")
    license: Optional[str] = Field(None, description="License of the server")


class ClientType(str, Enum):
    """Supported MCP client types."""
    CLAUDE_DESKTOP = "claude-desktop"
    CURSOR = "cursor"
    VSCODE = "vscode"
    CUSTOM = "custom"


class ConfiguredServerInfo(BaseModel):
    """Information about a configured MCP server."""
    name: str = Field(..., description="Name of the MCP server")
    environment_path: str = Field(..., description="Path to the conda environment")
    client: ClientType = Field(..., description="Client type")
    workspace_path: Optional[str] = Field(None, description="Workspace path if applicable")
    command: str = Field(..., description="Command to start the server")
    is_active: bool = Field(default=True, description="Whether the server is active")


class EnvironmentInfo(BaseModel):
    """Information about a conda environment for an MCP server."""
    name: str = Field(..., description="Name of the environment")
    path: str = Field(..., description="Path to the environment")
    server_name: str = Field(..., description="Name of the associated MCP server")
    python_version: str = Field(..., description="Python version in the environment")
    created_at: str = Field(..., description="Creation timestamp")
    last_updated: Optional[str] = Field(None, description="Last update timestamp")


class InstallationResult(BaseModel):
    """Result of an installation operation."""
    success: bool = Field(..., description="Whether the installation was successful")
    server_name: str = Field(..., description="Name of the server")
    environment_path: Optional[str] = Field(None, description="Path to the created environment")
    error_message: Optional[str] = Field(None, description="Error message if installation failed")
    config_path: Optional[str] = Field(None, description="Path to the updated configuration file")


class ActionPlan(BaseModel):
    """Action plan for conda operations."""
    action: str = Field(..., description="Type of action to perform")
    description: str = Field(..., description="Human-readable description of the action")
    environment: Optional[str] = Field(None, description="Target environment name")
    packages: Optional[List[str]] = Field(None, description="Packages to install or update")
    exclude: Optional[List[str]] = Field(None, description="Packages to exclude from updates")
    python_version: Optional[str] = Field(None, description="Python version for new environments")
    name: Optional[str] = Field(None, description="Name for new environments")
