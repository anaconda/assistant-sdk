from rich.markdown import CodeBlock
from rich.syntax import ANSISyntaxTheme
from rich.style import Style

from typing import Dict, Tuple
from pygments.token import (  # type: ignore
    Comment,
    Error,
    Generic,
    Keyword,
    Name,
    Number,
    Operator,
    String,
    Token,
    Whitespace,
)

# Note, can use either the `ansi_theme` or `ANSISyntaxThemeCustom()` for setting theme in `Syntax` constructor

TokenType = Tuple[str, ...]

"""
Borrowed from the rich algol theme
"""
style_map: Dict[TokenType, Style] = {
    Token: Style(color="cyan"),
    Whitespace: Style(),
    Comment: Style(dim=True),
    Comment.Preproc: Style(),
    Keyword: Style(bold=True, underline=True),
    Keyword.Type: Style(),
    Operator.Word: Style(),
    Name.Builtin: Style(bold=True),
    Name.Function: Style(bold=True, italic=True, dim=True),
    Name.Namespace: Style(underline=True),
    Name.Class: Style(dim=True, bold=True),
    Name.Exception: Style(),
    Name.Decorator: Style(),
    Name.Variable: Style(),
    Name.Constant: Style(),
    Name.Attribute: Style(),
    Name.Tag: Style(),
    String: Style(dim=True, italic=True),
    Number: Style(),
    Generic.Deleted: Style(color="bright_red"),
    Generic.Inserted: Style(color="green"),
    Generic.Heading: Style(bold=True),
    Generic.Subheading: Style(dim=True, bold=True),
    Generic.Prompt: Style(bold=True),
    Generic.Error: Style(color="bright_red"),
    Error: Style(color="red", underline=True),
}

ansi_theme = ANSISyntaxTheme(style_map=style_map)


class ANSISyntaxThemeCustom(ANSISyntaxTheme):
    def __init__(self) -> None:
        self._missing_style = Style.null()
        self._background_style = Style.null()

    def get_style_for_token(self, token_type: TokenType) -> Style:
        return Style(color="green")
