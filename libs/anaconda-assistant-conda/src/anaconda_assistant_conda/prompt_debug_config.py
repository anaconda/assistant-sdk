import sys
from rich.prompt import Prompt
from rich.console import Console

from .config import (
    AssistantCondaConfig,
    DebugErrorMode,
    set_debug_error_mode,
)

console = Console()

config_command_styled = "[reverse]conda assist config[/reverse]"


def prompt_debug_config() -> DebugErrorMode:
    """Configure eagerness of AI assistance when running conda commands"""

    mode: DebugErrorMode = None

    help_option = Prompt.ask(
        "\n[bold]Would you like [green]Anaconda Assistant[/green] to help resolve your errors?[/bold]\n"
        "\n"
        "Assistant is an AI-powered debugging tool for conda errors. Learn more here: \n"
        "https://anaconda.com/docs/tools/working-with-conda/cli-assistant\n"
        "\n"
        "[bold]Choose how you want the Assistant to help you:[/bold]\n"
        "1. Automated - Assistant will automatically provide solutions to errors as they occur.\n"
        "2. Ask first - Assistant will ask if you want help when you encounter errors.\n"
        "3. Disable - Assistant will not provide help with conda errors.\n"
        "\n"
        "[bold]Enter your choice[/bold]",
        choices=["1", "2", "3"],
    )

    # In the future, we might have "always" or "on" when we want to disable debug
    if help_option == "1":
        mode = "automatic"
    elif help_option == "2":
        mode = "ask"
    elif help_option == "3":
        mode = "off"

    set_debug_error_mode(mode)

    if mode == "automatic":
        console.print(
            f"\n✅ Assistant will automatically provide solutions. To change your selection, run {config_command_styled}\n"
        )
        return mode
    elif mode == "ask":
        console.print(
            f"\n✅ Assistant will ask if you want help when you encounter errors. To change your selection, run {config_command_styled}\n"
        )
        return mode
    elif mode == "off":
        console.print(
            f"\n✅ Assistant will not provide help with conda errors. To change your selection, run {config_command_styled}\n"
        )
        return mode
    return None
