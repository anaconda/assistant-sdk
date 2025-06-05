# MCP Manager - Core Exceptions

class MCPManagerError(Exception):
    """Base exception for MCP Manager errors."""
    pass

class EnvironmentCreationError(MCPManagerError):
    """Raised when creating a conda environment fails."""
    pass

class EnvironmentRemovalError(MCPManagerError):
    """Raised when removing a conda environment fails."""
    pass

class PackageInstallationError(MCPManagerError):
    """Raised when installing packages into an environment fails."""
    pass

class PackageUpdateError(MCPManagerError):
    """Raised when updating packages in an environment fails."""
    pass

class ServerNotFoundError(MCPManagerError):
    """Raised when a requested MCP server is not found in the catalog."""
    pass

class ServerAlreadyInstalledError(MCPManagerError):
    """Raised when attempting to install a server that is already installed."""
    pass

class ServerNotInstalledError(MCPManagerError):
    """Raised when attempting to update or uninstall a server that is not installed."""
    pass

class ConfigurationError(MCPManagerError):
    """Raised for errors related to reading or writing client configuration files."""
    pass

class ClientNotSupportedError(MCPManagerError):
    """Raised when an unsupported MCP client is specified."""
    pass

class CondaCommandError(MCPManagerError):
    """Raised when a generic conda command execution fails."""
    def __init__(self, command: str, return_code: int, stdout: str, stderr: str):
        self.command = command
        self.return_code = return_code
        self.stdout = stdout
        self.stderr = stderr
        # Improved error message formatting to clearly show the command and stderr
        super().__init__(f"Command '{self.command}' failed with code {self.return_code}. Stderr: {self.stderr}")

