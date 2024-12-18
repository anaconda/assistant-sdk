import sys
import traceback
from typing import Generator, Any

from anaconda_assistant.config import AssistantConfig
from conda import plugins, CondaError
from conda.cli.conda_argparse import BUILTIN_COMMANDS
from conda.exception_handler import ExceptionHandler
from conda.exceptions import PackagesNotFoundError
from rich.console import Console

from .config import AssistantCondaConfig
from .core import stream_response
from .cli import app

ENV_COMMANDS = {
    "env_config",
    "env_create",
    "env_export",
    "env_list",
    "env_remove",
    "env_update",
}

BUILD_COMMANDS = {
    "build",
    "convert",
    "debug",
    "develop",
    "index",
    "inspect",
    "metapackage",
    "render",
    "skeleton",
}

ALL_COMMANDS = BUILTIN_COMMANDS.union(ENV_COMMANDS, BUILD_COMMANDS)

console = Console()


ExceptionHandler._orig_print_conda_exception = (  # type: ignore
    ExceptionHandler._print_conda_exception
)


def error_handler(command: str) -> None:
    is_a_tty = sys.stdout.isatty()

    config = AssistantCondaConfig()
    if not config.suggest_correction_on_error:
        return

    assistant_config = AssistantConfig()
    if assistant_config.accepted_terms is False:
        return

    def assistant_exception_handler(
        self: ExceptionHandler,
        exc_val: CondaError,
        exc_tb: traceback.TracebackException,
    ) -> None:
        self._orig_print_conda_exception(exc_val, exc_tb)  # type: ignore
        if exc_val.return_code == 0:
            return

        elif command == "search" and isinstance(exc_val, PackagesNotFoundError):
            # When a package is not found it actually throws an error
            # it is perhaps better to recommend the new assist search.
            recommend_assist_search("search")
            return

        report = self.get_error_report(exc_val, exc_tb)

        console.print("[bold green]Hello from Anaconda Assistant![/green bold]")
        console.print("I'm going to help you diagnose and correct this error.")
        prompt = f"COMMAND:\n{report['command']}\nMESSAGE:\n{report['error']}"
        stream_response(config.system_messages.error, prompt, is_a_tty=is_a_tty)

    ExceptionHandler._print_conda_exception = assistant_exception_handler  # type: ignore


@plugins.hookimpl
def conda_subcommands() -> Generator[plugins.CondaSubcommand, None, None]:
    yield plugins.CondaSubcommand(
        name="assist",
        summary="Anaconda Assistant integration",
        action=lambda args: app(args=args),
    )


def recommend_assist_search(_: Any) -> None:
    console = Console(stderr=True)
    console.print("[bold green]Hello from Anaconda Assistant![/bold green]")
    console.print("If you're not finding what you're looking for try")
    console.print('  conda assist search "A package that can ..."')


@plugins.hookimpl
def conda_post_commands() -> Generator[plugins.CondaPostCommand, None, None]:
    yield plugins.CondaPostCommand(
        name="assist-search-recommendation",
        action=recommend_assist_search,
        run_for={"search"},
    )


@plugins.hookimpl
def conda_pre_commands() -> Generator[plugins.CondaPreCommand, None, None]:
    yield plugins.CondaPreCommand(
        name="error-handler", action=error_handler, run_for=ALL_COMMANDS
    )
