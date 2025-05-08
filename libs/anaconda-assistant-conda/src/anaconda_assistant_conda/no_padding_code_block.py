from rich.markdown import CodeBlock
from rich.prompt import Confirm
from rich.syntax import Syntax

from .ansi_theme import ANSISyntaxThemeCustom, theme


# Subclass CodeBlock to override the default padding
# Override default class:
# https://github.com/Textualize/rich/blob/6396050ad77d0de796107336aeeb5eeb7d030893/rich/markdown.py#L167
class NoPaddingCodeBlock(CodeBlock):
    def __rich_console__(self, console, options):
        original_code = str(self.text).rstrip()

        lines = original_code.split("\n")

        # Get the length of the longest line
        longest_line_length = max(len(line) for line in lines)

        # Add a space to the beginning of each line
        code = "\n".join("  " + line for line in lines)

        dashes = "-" * longest_line_length

        # code = "  " + dashes + "\n" + code + "\n  " + dashes

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


def override_markdown_formatting(Markdown):
    # Override the default CodeBlock with your custom one
    Markdown.elements["fence"] = NoPaddingCodeBlock
    Markdown.elements["code_block"] = NoPaddingCodeBlock
