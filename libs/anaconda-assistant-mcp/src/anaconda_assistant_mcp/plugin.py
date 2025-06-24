from typing import Generator

from conda import plugins
from .server import mcp_app


@plugins.hookimpl
def conda_subcommands() -> Generator[plugins.CondaSubcommand, None, None]:
    yield plugins.CondaSubcommand(
        name="mcp",
        summary="Anaconda Assistant integration",
        action=lambda args: mcp_app(args=args),
    )
