from typing import Generator, Any
import sys

from conda import plugins
from .server import mcp_app


@plugins.hookimpl
def conda_subcommands() -> Generator[plugins.CondaSubcommand, None, None]:
    def action(args: Any) -> Any:
        # Convert args to sys.argv format that Typer expects
        if args:
            sys.argv = ['mcp'] + list(args)
        else:
            sys.argv = ['mcp']
        return mcp_app()
    
    yield plugins.CondaSubcommand(
        name="mcp",
        summary="Anaconda Assistant integration",
        action=action,
    )
