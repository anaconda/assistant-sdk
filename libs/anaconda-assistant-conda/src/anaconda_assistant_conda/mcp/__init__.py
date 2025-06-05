"""
MCP (Model Context Protocol) integration for Anaconda Assistant.

This package provides MCP server management and integration with the Anaconda CLI Assistant.
"""

from typing import Dict, List, Optional, Any, Union

# Version information
__version__ = "0.1.0"

# Re-export key types and functions for easier imports
from .models import ServerInfo, ClientType, ActionPlan, InstallationResult
