# MCP Manager - Catalog Module

from typing import List, Dict, Optional
from anaconda_assistant_conda.mcp.core.exceptions import ServerNotFoundError

# Initial hardcoded list of known/approved MCP servers
# This structure can be expanded later (e.g., add descriptions, dependencies)
# In a real scenario, this might come from an API (like Anaconda PSM) or dynamic discovery.
HARDCODED_SERVERS = {
    "condamcp": {
        "package_name": "condamcp", # The conda package name to install - Requires manual install!
        "description": "An open-source Model Context Protocol (MCP) server for Conda.",
        "version": "0.1.0", # Example version, could be fetched dynamically later
        "source": "https://github.com/jnoller/condamcp" # Example source
    },
    "packaging-tools": {
        # Changed package_name to tqdm for demonstration purposes
        "package_name": "tqdm",
        "description": "MCP server providing package building and analysis tools (tqdm package)",
        "version": "N/A", # Version not relevant for demo package
        "source": "conda-forge" # Indicate where tqdm comes from
    },
    # Add more known servers here as needed
}

class Catalog:
    """Manages the discovery and information retrieval of MCP servers."""

    def __init__(self, catalog_url: Optional[str] = None):
        """Initializes the Catalog.

        Args:
            catalog_url: Optional URL for a dynamic catalog (not used in initial version).
        """
        self._catalog_url = catalog_url
        # In the future, could fetch from catalog_url if provided
        self._servers = HARDCODED_SERVERS

    def list_servers(self) -> List[Dict[str, str]]:
        """Returns a list of available MCP servers with basic info."""
        server_list = []
        for name, details in self._servers.items():
            server_list.append({
                "name": name,
                "description": details.get("description", "No description available."),
                "version": details.get("version", "N/A")
            })
        return server_list

    def get_server_details(self, server_name: str) -> Dict[str, str]:
        """Returns detailed information for a specific MCP server.

        Args:
            server_name: The name of the server.

        Returns:
            A dictionary containing server details.

        Raises:
            ServerNotFoundError: If the server_name is not found in the catalog.
        """
        if server_name not in self._servers:
            raise ServerNotFoundError(f"Server ","{","server_name","}"," not found in the catalog.")
        # Return a copy to prevent modification of internal state
        return self._servers[server_name].copy()

    def get_server_package_name(self, server_name: str) -> str:
        """Gets the conda package name for a given server.

        Args:
            server_name: The logical name of the server.

        Returns:
            The conda package name to install.

        Raises:
            ServerNotFoundError: If the server_name is not found.
        """
        details = self.get_server_details(server_name) # Handles not found error
        package_name = details.get("package_name")
        if not package_name:
            # This case should ideally not happen if catalog entries are well-formed
            raise ServerNotFoundError(f"Package name not defined for server ","{","server_name","}"," in catalog.")
        return package_name

