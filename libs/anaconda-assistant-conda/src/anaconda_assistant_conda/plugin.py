import sys
import traceback
from typing import Any, Generator
import pytest

from anaconda_assistant.config import AssistantConfig
from conda import CondaError, plugins
from conda.cli.conda_argparse import BUILTIN_COMMANDS
from conda.exception_handler import ExceptionHandler
from conda.exceptions import PackagesNotFoundError
from rich.console import Console
from rich.prompt import Confirm

from .cli import app
from .config import AssistantCondaConfig
from .core import stream_response
from .debug_config import debug_config, config_command_styled
from .get_clean_error_report_command import get_clean_error_report_command

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
    if config.debug_error_mode == "off":
        return

    assistant_config = AssistantConfig()
    if assistant_config.accepted_terms is False:
        return

    def assistant_exception_handler(
        self: ExceptionHandler,
        exc_val: CondaError,
        exc_tb: traceback.TracebackException,
    ) -> None:

        # conda is in the middle of executing something, and user types ctrl-c, we don't want to try and "fix"
        # the error since it's not really an error
        if str(exc_val) == "KeyboardInterrupt":
            console.print(
                "\n\n[bold red]Operation canceled by user (Ctrl-C).[/bold red]\n"
            )
            sys.exit(1)
        try:
            self._orig_print_conda_exception(exc_val, exc_tb)  # type: ignore
            if exc_val.return_code == 0:
                return

            report = self.get_error_report(exc_val, exc_tb)

            # print("\n-----exc_val-----\n")
            # print(exc_val)
            # print("\n-----exc_tb-----\n")
            # print(exc_tb)
            # print("\n-----report-----\n")
            # print(report)

            command = get_clean_error_report_command(report)
            prompt = f"COMMAND:\n{command}\nMESSAGE:\n{report['error']}"

            debug_mode = config.debug_error_mode

            # If we don't have a config option, we ask the user
            if debug_mode == None:
                debug_mode = debug_config()
            if debug_mode == "automatic":
                stream_response(config.system_messages.error, prompt, is_a_tty=is_a_tty)
            elif debug_mode == "ask":
                should_debug = Confirm.ask(
                    "[bold]Debug with Anaconda Assistant?[/bold]",
                )
                if should_debug == True:
                    stream_response(
                        config.system_messages.error, prompt, is_a_tty=is_a_tty
                    )
                else:
                    console.print(
                        "\nOK, goodbye! 👋\n"
                        f"To change default behavior, run {config_command_styled}\n"
                    )
        # If we're in the conda debug flow, ctrl-c is caught so we don't show stack trace
        except KeyboardInterrupt:
            console.print(
                "\n\n[bold red]Operation canceled by user (Ctrl-C).[/bold red]\n"
            )
            sys.exit(1)

    ExceptionHandler._print_conda_exception = assistant_exception_handler  # type: ignore


@plugins.hookimpl
def conda_subcommands() -> Generator[plugins.CondaSubcommand, None, None]:
    yield plugins.CondaSubcommand(
        name="assist",
        summary="Anaconda Assistant integration",
        action=lambda args: app(args=args),
    )


@plugins.hookimpl
def conda_pre_commands() -> Generator[plugins.CondaPreCommand, None, None]:
    yield plugins.CondaPreCommand(
        name="error-handler", action=error_handler, run_for=ALL_COMMANDS
    )
