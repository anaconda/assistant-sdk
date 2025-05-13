from rich.markdown import Markdown, CodeBlock
from rich.prompt import Confirm
from rich.syntax import Syntax

from .ansi_syntax_theme import ANSISyntaxThemeCustom


# Subclass CodeBlock to override the default padding
# Override default class:
# https://github.com/Textualize/rich/blob/6396050ad77d0de796107336aeeb5eeb7d030893/rich/markdown.py#L167
class NoPaddingCodeBlock(CodeBlock):
    def __rich_console__(self, console, options):  # type: ignore
        original_code = str(self.text).rstrip()

        lines = original_code.split("\n")

        # Add a space to the beginning of each line
        code = "\n".join("  " + line for line in lines)

        syntax = Syntax(
            code,
            self.lexer_name,
            theme=ANSISyntaxThemeCustom(),
            word_wrap=True,
            padding=0,  # Set padding to 0 instead of default 1
            background_color="default",  # Remove trailing spaces
            tab_size=2,
        )
        yield syntax


class MyMarkdown(Markdown):
    """Custom Markdown class to override default Markdown elements."""

    elements = Markdown.elements.copy()
    elements.update(
        {
            "fence": NoPaddingCodeBlock,
            "code_block": NoPaddingCodeBlock,
        }
    )
