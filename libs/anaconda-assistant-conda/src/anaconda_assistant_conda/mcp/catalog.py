"""
MCP (Model Context Protocol) - Catalog Module

This module handles the discovery and listing of available MCP servers.
"""
from typing import Dict, List, Optional

from .models import ServerInfo


class MCPCatalog:
    """
    Catalog of available MCP servers.
    
    This class manages the discovery and listing of available MCP servers.
    Initially, it uses a hardcoded list of approved servers, but future
    versions will support dynamic discovery from conda channels.
    """
    
    def __init__(self) -> None:
        """Initialize the catalog with a hardcoded list of approved servers."""
        # In a real implementation, this would be fetched from a remote source
        # or discovered dynamically from conda channels
        self._servers: Dict[str, ServerInfo] = {
            "packaging-tools": ServerInfo(
                name="packaging-tools",
                version="0.1.0",
                description="MCP server for conda packaging tools",
                dependencies=["conda", "conda-build", "conda-verify"],
                homepage="https://github.com/conda/packaging-tools-mcp",
                repository="https://github.com/conda/packaging-tools-mcp",
                author="Anaconda, Inc.",
                license="BSD-3-Clause"
            ),
            "condamcp": ServerInfo(
                name="condamcp",
                version="0.1.0",
                description="MCP server for conda environment and package management",
                dependencies=["conda", "mamba"],
                homepage="https://github.com/jnoller/condamcp",
                repository="https://github.com/jnoller/condamcp",
                author="Jesse Noller",
                license="BSD-3-Clause"
            ),
            "jupyter-mcp": ServerInfo(
                name="jupyter-mcp",
                version="0.1.0",
                description="MCP server for Jupyter notebooks",
                dependencies=["jupyter", "notebook", "jupyterlab"],
                homepage="https://github.com/jupyter/jupyter-mcp",
                repository="https://github.com/jupyter/jupyter-mcp",
                author="Jupyter Team",
                license="BSD-3-Clause"
            ),
            "data-science-tools": ServerInfo(
                name="data-science-tools",
                version="0.1.0",
                description="MCP server for data science tools",
                dependencies=["pandas", "numpy", "matplotlib", "scikit-learn"],
                homepage="https://github.com/anaconda/data-science-tools-mcp",
                repository="https://github.com/anaconda/data-science-tools-mcp",
                author="Anaconda, Inc.",
                license="BSD-3-Clause"
            ),
        }
    
    def list_available_servers(self) -> List[ServerInfo]:
        """
        List all available MCP servers from the catalog.
        
        Returns:
            List[ServerInfo]: List of available servers
        """
        return list(self._servers.values())
    
    def get_server_details(self, server_name: str) -> Optional[ServerInfo]:
        """
        Get detailed information about a specific server.
        
        Args:
            server_name: Name of the server to get details for
            
        Returns:
            Optional[ServerInfo]: Server details if found, None otherwise
        """
        return self._servers.get(server_name)
    
    def search_servers(self, query: str) -> List[ServerInfo]:
        """
        Search for servers matching the query.
        
        Args:
            query: Search query string
            
        Returns:
            List[ServerInfo]: List of servers matching the query
        """
        query = query.lower()
        results = []
        
        for server in self._servers.values():
            # Search in name, description, and dependencies
            if (query in server.name.lower() or 
                query in server.description.lower() or 
                any(query in dep.lower() for dep in server.dependencies)):
                results.append(server)
                
        return results
