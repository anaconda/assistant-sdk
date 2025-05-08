import sys
from rich.prompt import Prompt
from rich.console import Console

from .core import set_config
from .config import AssistantCondaConfig

console = Console()
conf = AssistantCondaConfig()

config_command_styled = "[reverse]conda assist configure[/reverse]"


def debug_config():
    """Configure eagerness of AI assistance when running conda commands"""

    debug_mode = conf.debug_error_mode

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
    elif help_option == "2":
        debug_mode = "ask"
    elif help_option == "3":
        debug_mode = "off"

    set_config("plugin.assistant", "debug_error_mode", debug_mode)

    if debug_mode == "automatic":
        console.print(
            f"\n✅ Assistant will automatically provide solutions. To change your selection, run {config_command_styled}\n"
        )
        return debug_mode
    elif debug_mode == "ask":
        console.print(
            f"\n✅ Assistant will ask if you want help when you encounter errors. To change your selection, run {config_command_styled}\n"
        )
        return debug_mode
    elif debug_mode == "off":
        console.print(
            f"\n✅ Assistant will not provide help with conda errors. To change your selection, run {config_command_styled}\n"
        )
        return debug_mode
