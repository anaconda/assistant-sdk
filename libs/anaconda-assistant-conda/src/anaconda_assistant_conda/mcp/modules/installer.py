# MCP Manager - Installer Module

from typing import List, Optional
from anaconda_assistant_conda.mcp.modules import conda_utils
# Import specific exceptions directly
from anaconda_assistant_conda.mcp.core.exceptions import PackageInstallationError, PackageUpdateError

class Installer:
    """Handles installation and updates of MCP server packages within their environments."""

    def install_server_package(self, prefix: str, package_name: str, channel: Optional[str] = None) -> None:
        """Installs the MCP server package into its dedicated environment.

        Args:
            prefix: The absolute path (prefix) of the target environment.
            package_name: The name of the conda package to install.
            channel: Optional channel to use for installation.

        Raises:
            PackageInstallationError: If the installation fails.
        """
        print(f"Installing package {package_name} into {prefix}...")
        try:
            conda_utils.install_packages(prefix=prefix, packages=[package_name], channel=channel)
            print(f"Package {package_name} installed successfully.")
        except Exception as e:
            # Catch specific conda errors if needed, re-raise as PackageInstallationError
            raise PackageInstallationError(f"Failed to install {package_name} into {prefix}: {e}") from e

    def update_server_package(self, prefix: str, package_name: str) -> None:
        """Updates the MCP server package in its dedicated environment.

        Args:
            prefix: The absolute path (prefix) of the target environment.
            package_name: The name of the conda package to update.

        Raises:
            PackageUpdateError: If the update fails.
        """
        print(f"Updating package {package_name} in {prefix}...")
        try:
            # Update the specific package
            conda_utils.update_packages(prefix=prefix, packages=[package_name])
            # Alternatively, could update all packages in the env:
            # conda_utils.update_packages(prefix=prefix, update_all=True)
            print(f"Package {package_name} updated successfully.")
        except Exception as e:
            raise PackageUpdateError(f"Failed to update {package_name} in {prefix}: {e}") from e


