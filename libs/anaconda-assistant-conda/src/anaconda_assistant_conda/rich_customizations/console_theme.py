from rich.style import Style
from rich.theme import Theme

console_theme = Theme(
    {
        "prompt.choices": "bold green italic",  # Style for the choices
        "prompt.default": "italic yellow",  # Style for the default value
        "prompt.invalid": "bold red",  # Style for error messages
        "markdown.code": Style(bold=True, color="cyan", bgcolor="black"),
        "markdown.code_block": Style(color="cyan", bgcolor="black"),
    }
)
