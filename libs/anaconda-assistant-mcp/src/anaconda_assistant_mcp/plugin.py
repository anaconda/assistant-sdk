from typing import Generator

from conda import plugins

from .server import mcp_app
from .experiments.server_experiments import mcp_app_experiments


@plugins.hookimpl
def conda_subcommands() -> Generator[plugins.CondaSubcommand, None, None]:
    yield plugins.CondaSubcommand(
        name="mcp",
        summary="Anaconda Assistant integration",
        action=lambda args: mcp_app(args=args),
    )


@plugins.hookimpl
def conda_subcommands() -> Generator[plugins.CondaSubcommand, None, None]:
    yield plugins.CondaSubcommand(
        name="mcp-experiments",
        summary="Anaconda Assistant integration",
        action=lambda args: mcp_app_experiments(args=args),
    )
