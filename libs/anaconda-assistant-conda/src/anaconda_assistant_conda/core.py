import typer
from anaconda_assistant import ChatSession
from anaconda_cli_base.cli import ErrorHandledGroup
from rich.console import Console
from rich.live import Live
from rich.markdown import Markdown
from typing_extensions import Annotated

console = Console()


def stream_response(system_message, prompt) -> None:
    fake_app = typer.Typer(
        help="fake app to support error handling", cls=ErrorHandledGroup
    )

    @fake_app.callback(name="chat", invoke_without_command=True, cls=ErrorHandledGroup)
    def chat(
        system_message: Annotated[str, typer.Argument],
        prompt: Annotated[str, typer.Argument],
    ):
        full_text = ""
        with Live(
            Markdown(full_text),
            auto_refresh=False,
            vertical_overflow="visible",
            console=console,
        ) as live:
            session = ChatSession(system_message=system_message)
            response = session.chat(prompt, stream=True)

            for chunk in response:
                full_text += chunk
                md = Markdown(full_text)
                live.update(md, refresh=True)

    fake_app(args=(system_message, prompt))
