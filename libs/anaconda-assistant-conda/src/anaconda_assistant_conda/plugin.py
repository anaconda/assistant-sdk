import sys
import traceback
from typing import Any, Generator

from anaconda_assistant.config import AssistantConfig
from conda import CondaError, plugins
from conda.cli.conda_argparse import BUILTIN_COMMANDS
from conda.exception_handler import ExceptionHandler
from conda.exceptions import PackagesNotFoundError
from rich.console import Console
from rich.prompt import Confirm

from .cli import app
from .config import AssistantCondaConfig, DebugErrorMode
from .core import stream_response
from .prompt_debug_config import prompt_debug_config, config_command_styled
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


def create_message(
    debug_mode: DebugErrorMode,
    prompt: str,
    is_a_tty: bool = True,
    error: str = "",
) -> None:
    # If we don't have a config option, we ask the user
    if debug_mode is None:
        debug_mode = prompt_debug_config()
    elif debug_mode == "automatic":
        stream_response(error, prompt, is_a_tty=is_a_tty)
    elif debug_mode == "ask":
        should_debug = Confirm.ask(
            "[bold]Debug with Anaconda Assistant?[/bold]",
        )
        if should_debug:
            stream_response(error, prompt, is_a_tty=is_a_tty)
        else:
            console.print(
                "\nOK, goodbye! 👋\n"
                f"To change default behavior, run {config_command_styled}\n"
            )


def error_handler(command: str) -> None:
    interrupt_message_styled = (
        "\n\n[bold red]Operation canceled by user (Ctrl-C).[/bold red]\n"
    )

    def assistant_exception_handler(
        self: ExceptionHandler,
        exc_val: CondaError,
        exc_tb: traceback.TracebackException,
    ) -> None:

        # If conda is in the middle of executing something, and user types ctrl-c, we don't want to try and "fix"
        # the error since it's not really an error, so we just re-throw.
        # This also prevents stack trace from being printed.
        if str(exc_val) == "KeyboardInterrupt":
            console.print(interrupt_message_styled)
            sys.exit(1)

        try:
            self._orig_print_conda_exception(exc_val, exc_tb)  # type: ignore
            if exc_val.return_code == 0:
                return

            try:
                config = AssistantCondaConfig()
                if config.debug_error_mode == "off":
                    return

                # If the user has not accepted the terms, we prompt them to do so.
                # This would tend to happen if the user manually modified the config file.
                assistant_config = AssistantConfig()
                if assistant_config.accepted_terms is False:
                    from .prompt_accept_terms import prompt_accept_terms

                    if not sys.stdout.isatty():
                        console.print(
                            "\nYou must accept the terms to use Anaconda Assistant.\n"
                        )
                        return
                    accepted = prompt_accept_terms()
                    if accepted:
                        console.print(
                            "\nThank you! Run the previous command again to see your change reflected.\n"
                        )
                    else:
                        console.print(
                            "\n[bold red]You must accept the terms to use Anaconda Assistant.[/bold red]\n"
                        )
                    return
            except Exception as e:
                from anaconda_cli_base.config import anaconda_config_path

                print("Anaconda Assistant is not configured correctly. ")
                print(f"Error in {anaconda_config_path()}")
                print(repr(e))
                sys.exit(1)

            report = self.get_error_report(exc_val, exc_tb)
            command = get_clean_error_report_command(report)
            prompt = f"COMMAND:\n{command}\nMESSAGE:\n{report['error']}"
            is_a_tty = sys.stdout.isatty()
            error = config.system_messages.error

            create_message(config.debug_error_mode, prompt, is_a_tty, error)

        # If we're in the conda debug flow, ctrl-c is caught so we don't show stack trace.
        # This also prevents stack trace from being printed.
        except KeyboardInterrupt:
            console.print(interrupt_message_styled)
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
