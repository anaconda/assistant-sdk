# MCP Manager - Core Service

from typing import List, Dict, Optional, Any

from anaconda_assistant_conda.mcp.settings import get_settings
from anaconda_assistant_conda.mcp.modules.catalog import Catalog
from anaconda_assistant_conda.mcp.modules.environment import EnvironmentManager
from anaconda_assistant_conda.mcp.modules.installer import Installer
from anaconda_assistant_conda.mcp.modules.config.manager import ConfigManager
from anaconda_assistant_conda.mcp.core.exceptions import (
    MCPManagerError,
    ServerNotFoundError,
    ServerAlreadyInstalledError,
    ServerNotInstalledError,
    EnvironmentCreationError,
    EnvironmentRemovalError,
    PackageInstallationError,
    PackageUpdateError,
    ConfigurationError,
    ClientNotSupportedError
)

class MCPManagerService:
    """Orchestrates MCP server management operations."""

    def __init__(self) -> None:
        self.settings = get_settings()
        self.catalog = Catalog(catalog_url=self.settings.catalog_url)
        self.env_manager = EnvironmentManager()
        self.installer = Installer()
        self.config_manager = ConfigManager()

    def list_available_servers(self) -> List[Dict[str, str]]:
        """Lists servers available in the catalog."""
        return self.catalog.list_servers()

    def get_server_info(self, server_name: str) -> Dict[str, str]:
        """Gets detailed information for a specific server from the catalog."""
        try:
            return self.catalog.get_server_details(server_name)
        except ServerNotFoundError as e:
            raise e # Re-raise for CLI to handle

    def install_server(
        self, server_name: str, client_name: str, workspace_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """Installs an MCP server: creates env, installs package, updates config."""
        print(f"Starting installation process for server {server_name}...")
        prefix = self.env_manager.get_environment_prefix(server_name)

        # 1. Check if already installed (environment exists)
        if self.env_manager.environment_exists(server_name):
            raise ServerAlreadyInstalledError(
                f"Server {server_name} appears to be already installed at {prefix}. Use update or uninstall."
            )

        # 2. Get server details (package name) from catalog
        try:
            package_name = self.catalog.get_server_package_name(server_name)
            server_details = self.catalog.get_server_details(server_name)
            # Potentially use channel info from details later
        except ServerNotFoundError as e:
            raise e

        # 3. Create environment
        try:
            self.env_manager.create_environment(server_name)
        except EnvironmentCreationError as e:
            raise e

        # 4. Install package into environment
        try:
            self.installer.install_server_package(prefix=prefix, package_name=package_name)
        except PackageInstallationError as e:
            # Attempt to clean up the partially created environment
            print(f"Installation failed. Attempting to remove partially created environment at {prefix}...")
            try:
                self.env_manager.remove_environment(server_name)
            except EnvironmentRemovalError as cleanup_e:
                print(f"Warning: Failed to cleanup environment after installation error: {cleanup_e}")
            raise e # Re-raise the original installation error

        # 5. Update client configuration
        try:
            self.config_manager.add_server_config(
                server_name=server_name,
                server_prefix=prefix,
                client_name=client_name,
                workspace_path=workspace_path
            )
        except (ConfigurationError, ClientNotSupportedError) as e:
            # Config update failed, but installation succeeded. Should we roll back?
            # For now, report success with a warning about config.
            print(f"Warning: Server {server_name} installed, but failed to update client configuration: {e}")
            # Consider adding a rollback mechanism or clearer user guidance here.
            # raise e # Or re-raise to indicate partial failure

        print(f"Server {server_name} installed successfully.")
        return {"status": "success", "server_name": server_name, "prefix": prefix}

    def uninstall_server(
        self, server_name: str, client_name: str, workspace_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """Uninstalls an MCP server: removes config, removes env."""
        print(f"Starting uninstallation process for server {server_name}...")
        prefix = self.env_manager.get_environment_prefix(server_name)

        # 1. Check if environment exists
        if not self.env_manager.environment_exists(server_name):
            # Check config anyway, maybe it was partially removed
            print(f"Warning: Environment for server {server_name} not found at {prefix}. Checking configuration...")
            # raise ServerNotInstalledError(f"Server {server_name} environment not found at {prefix}.")

        # 2. Remove client configuration first
        config_removed = False
        try:
            self.config_manager.remove_server_config(
                server_name=server_name,
                client_name=client_name,
                workspace_path=workspace_path
            )
            config_removed = True # Assume success if no exception
        except (ConfigurationError, ClientNotSupportedError) as e:
            # Log error but proceed with environment removal if possible
            print(f"Warning: Failed to remove client configuration for {server_name}: {e}. Attempting environment removal anyway.")

        # 3. Remove environment
        env_removed = False
        if self.env_manager.environment_exists(server_name):
            try:
                self.env_manager.remove_environment(server_name)
                env_removed = True
            except EnvironmentRemovalError as e:
                # If config removal succeeded but env removal failed, report partial failure
                if config_removed:
                    raise MCPManagerError(f"Removed configuration for {server_name}, but failed to remove environment: {e}") from e
                else:
                    raise e # Both failed or only env removal failed
        elif not config_removed:
             # Neither env existed nor config was removed (or failed)
             raise ServerNotInstalledError(f"Server {server_name} not found (neither environment nor configuration entry). Nothing to uninstall.")

        print(f"Server {server_name} uninstalled successfully.")
        return {"status": "success", "server_name": server_name}

    def update_server(
        self, server_name: str, client_name: Optional[str] = None, workspace_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """Updates an installed MCP server package."""
        print(f"Starting update process for server {server_name}...")
        prefix = self.env_manager.get_environment_prefix(server_name)

        # 1. Check if installed (environment exists)
        if not self.env_manager.environment_exists(server_name):
            raise ServerNotInstalledError(f"Server {server_name} environment not found at {prefix}. Cannot update.")

        # 2. Get package name from catalog
        try:
            package_name = self.catalog.get_server_package_name(server_name)
        except ServerNotFoundError as e:
            # Server exists locally but not in catalog? Log warning and maybe try updating anyway?
            print(f"Warning: Server {server_name} found locally but not in catalog. Update may fail or use incorrect package name.")
            # Attempt to guess package name? Risky. For now, raise error.
            raise e

        # 3. Update package in environment
        try:
            self.installer.update_server_package(prefix=prefix, package_name=package_name)
        except PackageUpdateError as e:
            raise e

        print(f"Server {server_name} updated successfully.")
        return {"status": "success", "server_name": server_name, "prefix": prefix}

    def list_installed_servers(self, client_name: Optional[str] = None, workspace_path: Optional[str] = None) -> List[Dict[str, Any]]:
        """Lists installed MCP servers based on environments and optionally configuration."""
        installed_envs = self.env_manager.list_installed_environments()
        server_status_list = []

        # Get configured servers if client is specified
        configured_servers = {}
        if client_name:
            try:
                configured_list = self.config_manager.get_installed_servers_from_config(client_name, workspace_path)
                configured_servers = {s["name"]: s["path"] for s in configured_list}
            except (ConfigurationError, ClientNotSupportedError) as e:
                print(f"Warning: Could not read configuration for client {client_name}: {e}")

        # Correlate environments with catalog and config
        for server_name, prefix in installed_envs.items():
            status = {"name": server_name, "prefix": prefix, "status": "Installed (Environment Found)"}
            try:
                details = self.catalog.get_server_details(server_name)
                status["version"] = details.get("version", "N/A")
                status["description"] = details.get("description", "")
            except ServerNotFoundError:
                status["status"] = "Installed (Environment Found, Unknown in Catalog)"

            if client_name:
                if server_name in configured_servers:
                    if configured_servers[server_name] == prefix:
                        status["configured_for_client"] = "True"
                    else:
                        status["configured_for_client"] = f"Mismatch (Expected: {configured_servers[server_name]})"
                else:
                    status["configured_for_client"] = "False"

            server_status_list.append(status)

        # Add configured servers that don't have a corresponding environment (partial state)
        if client_name:
            for server_name, config_prefix in configured_servers.items():
                if server_name not in installed_envs:
                    status = {
                        "name": server_name,
                        "prefix": config_prefix,
                        "status": "Configured (Environment Missing)",
                        "configured_for_client": "True"
                    }
                    server_status_list.append(status)

        return server_status_list


