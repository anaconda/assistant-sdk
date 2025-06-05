# MCP Client Exceptions

class MCPClientError(Exception):
    """Base exception for MCP client errors."""
    pass

class ServerConnectionError(MCPClientError):
    """Raised when the client cannot connect to the MCP server."""
    pass

class ServerResponseError(MCPClientError):
    """Raised when the server returns an unexpected or error response."""
    pass

class ProtocolError(MCPClientError):
    """Raised when there is a mismatch in the expected MCP protocol."""
    pass

class ServerDiscoveryError(MCPClientError):
    """Raised when the client cannot find connection details for the server."""
    pass

