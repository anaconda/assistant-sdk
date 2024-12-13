import sys

from conda import plugins, CondaError
from conda.cli.conda_argparse import BUILTIN_COMMANDS
from conda.exception_handler import ExceptionHandler
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


console = Console()


def error_handler(_) -> None:
    is_a_tty = sys.stdout.isatty()

    config = AssistantCondaConfig()
    if not config.suggest_correction_on_error:
        return

    ExceptionHandler._orig_print_conda_exception = (
        ExceptionHandler._print_conda_exception
    )

    def assistant_exception_handler(self, exc_val: CondaError, exc_tb):
        self._orig_print_conda_exception(exc_val, exc_tb)
        if exc_val.return_code == 0:
            return

        report = self.get_error_report(exc_val, exc_tb)

        console.print("[bold green]Hello from Anaconda Assistant![/green bold]")
        console.print("I'm going to help you diagnose and correct this error.")
        prompt = f"COMMAND:\n{report['command']}\nMESSAGE:\n{report['error']}"
        stream_response(config.system_messages.error, prompt, is_a_tty=is_a_tty)

    ExceptionHandler._print_conda_exception = assistant_exception_handler


@plugins.hookimpl
def conda_subcommands():
    yield plugins.CondaSubcommand(
        name="assist",
        summary="Anaconda Assistant integration",
        action=lambda args: app(args=args),
    )


def recommend_assist_search(_) -> None:
    console = Console(stderr=True)
    console.print("[bold green]Hello from Anaconda Assistant![/bold green]")
    console.print("If you're not finding what you're looking for try")
    console.print('  conda assist search "A package that can ..."')


@plugins.hookimpl
def conda_post_commands():
    yield plugins.CondaPostCommand(
        name="assist-search-recommendation",
        action=recommend_assist_search,
        run_for={"search"},
    )


@plugins.hookimpl
def conda_pre_commands():
    yield plugins.CondaPreCommand(
        name="error-handler",
        action=error_handler,
        run_for=BUILTIN_COMMANDS.union(ENV_COMMANDS, BUILD_COMMANDS),
    )
