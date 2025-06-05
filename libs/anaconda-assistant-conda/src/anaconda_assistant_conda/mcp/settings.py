# MCP Manager - Settings

from anaconda_cli_base.config import AnacondaBaseSettings
from pydantic import Field
from typing import Optional, Dict
import os

# Define the default directory for MCP environments relative to the user's home
DEFAULT_MCP_DIR = os.path.join(os.path.expanduser("~"), ".anaconda", "mcp")

class MCPManagerSettings(AnacondaBaseSettings, plugin_name="mcp_manager"):
    """Settings specific to the MCP Manager plugin."""

    mcp_environment_path: str = Field(
        default=DEFAULT_MCP_DIR,
        description="The base directory where MCP server environments will be created."
    )
    # Add other potential settings here, e.g., default client, catalog URL
    default_client: Optional[str] = Field(
        default=None,
        description="Default MCP client to use if --client is not specified."
    )
    catalog_url: Optional[str] = Field(
        default=None, # Initially use hardcoded/PSM, this allows future override
        description="URL for the MCP server catalog."
    )

# Function to get current settings
def get_settings() -> MCPManagerSettings:
    """Loads and returns the current MCP Manager settings."""
    return MCPManagerSettings()


