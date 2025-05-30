from rich.prompt import Confirm
from textwrap import dedent
from .core import set_config


def prompt_accept_terms() -> int:
    msg = dedent(
        """\
        You have not accepted the terms of service.
        You must accept our terms of service and Privacy Policy here

          https://anaconda.com/legal

        [bold green]Are you more than 13 years old and accept the terms?[/bold green]"""
    )
    accepted_terms = Confirm.ask(msg)
    set_config("plugin.assistant", "accepted_terms", accepted_terms)
    return accepted_terms
