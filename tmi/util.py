import os
import time

from rich.console import Console
from rich.highlighter import RegexHighlighter
from rich.panel import Panel
from rich.text import Text
from rich.theme import Theme


def get_env(name, message, cast=str, is_password=False):
    """Resolve env variable if exists or get it from stdin

    Args:
        name (str): The env name
        message (str): The message to print in stdout
        cast (object, optional): Cast output to
        is_password: (bool, optional): Hide typed text. Defaults to False.

    Returns:
        object: Text read from stdin or resolved env.
    """
    console = get_console()
    if name in os.environ:
        return os.environ[name]
    while True:
        value = console.input(Text(message, style="repr.text"), password=is_password)
        try:
            return cast(value)
        except ValueError:
            log("warning", "Should be type of " + str(cast.__name__) + ".")
            time.sleep(1)

# pylint: disable=too-few-public-methods
def get_console():
    """Create and configure default console output formatter

    Returns:
        Console: Configured console instance.
    """

    class Highlighter(RegexHighlighter):
        """Apply style to matched text with defined regexps."""

        base_style = "repr."
        highlights = [
            r"(?P<info>\[INFO\])",
            r"(?P<success>\[SUCCESS\])",
            r"(?P<warning>\[WARNING\])",
            r"(?P<error>\[ERROR\])",
            r"(?P<text> [\w\-\(\)\.]+)",
            r"(?P<symbol>[\.,;:\-\!])",
            r"(?P<command> \w+\+\w+)",
        ]

    theme = Theme(
        {
            "repr.info": "cyan",
            "repr.warning": "yellow",
            "repr.error": "bold red",
            "repr.success": "green",
            "repr.text": "grey63",
            "repr.command": "cyan",
            "repr.symbol": "gray62",
        }
    )
    console = Console(highlighter=Highlighter(), theme=theme)
    return console
# pylint: enable=too-few-public-methods


def log(panel_type, message):
    """Format and log given message.

    Args:
        panel_type ("info"|"success"|"warning"|"error"): The env name
        message (str): The message to print in stdout

    Returns:
        void
    """

    def get_panel(panel_type, message):
        return Panel(
            f"[{panel_type.upper()}] " + message,
            title=None,
            title_align="left",
            subtitle="↓",
            subtitle_align="left",
            border_style=f"repr.{panel_type}",
            highlight=True,
            padding=1,
        )

    get_console().print(get_panel(panel_type, message))