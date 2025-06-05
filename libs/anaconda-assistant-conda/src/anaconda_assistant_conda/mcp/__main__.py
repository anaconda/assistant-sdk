"""
Main entry point for MCP module when run as a package.

This allows running the MCP CLI using:
python -m anaconda_assistant_conda.mcp
"""

from .cli import main

if __name__ == "__main__":
    main()
