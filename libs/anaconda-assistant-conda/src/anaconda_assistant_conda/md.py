import rich
from rich.markdown import Markdown
from rich.console import Console
from rich.color import Color

from .custom_theme import custom_theme
from .no_padding_code_block import override_markdown_formatting

override_markdown_formatting(Markdown)

console = Console(theme=custom_theme)

markdown = """\
Deserunt labore do elit mollit ut. Dolore Lorem quis non esse id nisi proident id esse tempor Lorem amet exercitation. Qui laborum ut mollit laborum proident. Qui elit mollit cupidatat ipsum. Voluptate aliquip elit consectetur dolor voluptate. Dolor labore est consectetur ipsum officia adipisicing eiusmod eiusmod velit dolor sunt sit labore. Qui cupidatat ea consequat adipisicing Lorem nostrud dolore. Aliqua dolore non magna Lorem elit nulla quis ullamco mollit ad mollit labore eiusmod. Non qui amet ipsum aliqua consequat nisi veniam officia. Id quis labore minim consectetur consectetur enim culpa quis cupidatat cupidatat voluptate aute non. Esse aute fugiat do eu excepteur sint dolore Lorem dolor.

This is some code:

```py
from typing import Iterator

# This is an example
class Math:
    @staticmethod
    def fib(n: int) -> Iterator[int]:
        \"\"\"Fibonacci series up to n.\"\"\"
        a, b = 0, 1
        while a < n:
            yield a
            a, b = b, a + b

result = sum(Math.fib(42))
print(f"The answer is {result}")

```

This is a line with inline code `conda install pandas`

Deserunt labore do elit mollit ut. Dolore Lorem quis non esse id nisi proident id esse tempor Lorem amet exercitation. Qui laborum ut mollit laborum proident. Qui elit mollit cupidatat ipsum. Voluptate aliquip elit consectetur dolor voluptate. Dolor labore est consectetur ipsum officia adipisicing eiusmod eiusmod velit dolor sunt sit labore. Qui cupidatat ea consequat adipisicing Lorem nostrud dolore. Aliqua dolore non magna Lorem elit nulla quis ullamco mollit ad mollit labore eiusmod. Non qui amet ipsum aliqua consequat nisi veniam officia. Id quis labore minim consectetur consectetur enim culpa quis cupidatat cupidatat voluptate aute non. Esse aute fugiat do eu excepteur sint dolore Lorem dolor.
"""

console.print(Markdown(markdown))
