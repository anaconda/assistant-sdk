import sys
import traceback
from typing import Any, Generator

from anaconda_assistant.config import AssistantConfig
from conda import CondaError, plugins
from conda.cli.conda_argparse import BUILTIN_COMMANDS
from conda.exception_handler import ExceptionHandler
from conda.exceptions import PackagesNotFoundError
from rich.console import Console
from rich.padding import Padding
from rich.prompt import Confirm, Prompt

from .cli import app
from .config import AssistantCondaConfig
from .core import stream_response, set_config, get_config

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
        config_command_styled = "[reverse]conda assist configure[/reverse]"

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

            elif command == "search" and isinstance(exc_val, PackagesNotFoundError):
                # When a package is not found it actually throws an error
                # it is perhaps better to recommend the new assist search.
                recommend_assist_search("search")
                return

            report = self.get_error_report(exc_val, exc_tb)
            prompt = f"COMMAND:\n{report['command']}\nMESSAGE:\n{report['error']}"

            debug_mode = get_config("plugin.assistant", "debug_error_mode")

            # If we don't have a config option, we ask the user
            if debug_mode == None:
                help_option = Prompt.ask(
                    "\n[bold]Would you like [green]Anaconda Assistant[/green] to help resolve your errors?[/bold]\n"
                    "\n"
                    "Assistant is an AI-powered debugging tool for conda errors. Learn more here: \n"
                    "https://anaconda.github.io/assistant-sdk/conda\n"
                    "\n"
                    "[bold]Choose how you want the Assistant to help you:[/bold]\n"
                    "1. Automated - Assistant will automatically provide solutions to errors as they occur.\n"
                    "2. Ask first - Assistant will ask if you want help when you encounter errors.\n"
                    "3. Disable - Assistant will not provide help with conda errors.\n"
                    "\n"
                    "[bold]Enter your choice[/bold]",
                    choices=["1", "2", "3"],
                )
                if help_option == "1":
                    debug_mode = "automatic"
                    set_config("plugin.assistant", "debug_error_mode", "automatic")
                elif help_option == "2":
                    debug_mode = "ask"
                    set_config("plugin.assistant", "debug_error_mode", "ask")
                elif help_option == "3":
                    debug_mode = "off"
                    set_config("plugin.assistant", "debug_error_mode", "off")

            if debug_mode == "automatic":
                console.print(
                    f"\n✅ Assistant will automatically provide solutions. To change your selection, run {config_command_styled}\n"
                )
                stream_response(config.system_messages.error, prompt, is_a_tty=is_a_tty)
            elif debug_mode == "ask":
                console.print(
                    f"\n✅ Assistant will ask if you want help when you encounter errors. To change your selection, run {config_command_styled}\n"
                )
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
            elif debug_mode == "off":
                console.print(
                    f"\n✅ Assistant will not provide help with conda errors. To change your selection, run {config_command_styled}\n"
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
