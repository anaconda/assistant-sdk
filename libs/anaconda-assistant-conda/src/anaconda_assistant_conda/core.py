from unittest.mock import patch

from anaconda_cli_base.exceptions import ERROR_HANDLERS
from anaconda_assistant import ChatSession
from rich.console import Console
from rich.live import Live
from rich.markdown import Markdown

console = Console()


def stream_response(system_message: str, prompt: str, is_a_tty: bool = True) -> None:
    full_text = ""
    with Live(
        Markdown(full_text),
        auto_refresh=False,
        vertical_overflow="visible",
        console=console,
    ) as live:
        with patch("anaconda_cloud_auth.cli.sys") as mocked:
            mocked.stdout.isatty.return_value = is_a_tty
            try:
                session = ChatSession(system_message=system_message)
                response = session.chat(message=prompt, stream=True)
            except Exception as e:
                callback = ERROR_HANDLERS[type(e)]
                exit_code = callback(e)
                if exit_code == -1:
                    session = ChatSession(system_message=system_message)
                    response = session.chat(prompt, stream=True)
                else:
                    return

            for chunk in response:
                full_text += chunk
                md = Markdown(full_text)
                live.update(md, refresh=True)
