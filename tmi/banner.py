from rich.align import Align
from rich.markdown import Markdown
from rich.padding import Padding
from rich.panel import Panel

from .util import get_console


def prompt():
    """Application Banner"""

    remarks_message = """
# Remarks:
1. Admin privileges or privilege to add member (in target group) is required for the client.
1. "A wait of n seconds is required (caused by InviteToChannelRequest)" is a known problem that caused by the limitation 
    of the telegram for clients who act like a bot.
1. You need to have the target group ID (It should be something similar to username).
"""
    welcome_message = """
                         ██████╗██████╗  █████╗ ██╗    ██╗██╗     ██╗███╗   ██╗ ██████╗
                        ██╔════╝██╔══██╗██╔══██╗██║    ██║██║     ██║████╗  ██║██╔════╝
                        ██║     ██████╔╝███████║██║ █╗ ██║██║     ██║██╔██╗ ██║██║  ███╗
                        ██║     ██╔══██╗██╔══██║██║███╗██║██║     ██║██║╚██╗██║██║   ██║
                        ╚██████╗██║  ██║██║  ██║╚███╔███╔╝███████╗██║██║ ╚████║╚██████╔╝
                         ╚═════╝╚═╝  ╚═╝╚═╝  ╚═╝ ╚══╝╚══╝ ╚══════╝╚═╝╚═╝  ╚═══╝ ╚═════╝

     ██████╗ ██████╗  ██████╗ ██╗   ██╗██████╗     ███╗   ███╗███████╗███╗   ███╗██████╗ ███████╗██████╗ ███████╗
    ██╔════╝ ██╔══██╗██╔═══██╗██║   ██║██╔══██╗    ████╗ ████║██╔════╝████╗ ████║██╔══██╗██╔════╝██╔══██╗██╔════╝
    ██║  ███╗██████╔╝██║   ██║██║   ██║██████╔╝    ██╔████╔██║█████╗  ██╔████╔██║██████╔╝█████╗  ██████╔╝███████╗
    ██║   ██║██╔══██╗██║   ██║██║   ██║██╔═══╝     ██║╚██╔╝██║██╔══╝  ██║╚██╔╝██║██╔══██╗██╔══╝  ██╔══██╗╚════██║
    ╚██████╔╝██║  ██║╚██████╔╝╚██████╔╝██║         ██║ ╚═╝ ██║███████╗██║ ╚═╝ ██║██████╔╝███████╗██║  ██║███████║
     ╚═════╝ ╚═╝  ╚═╝ ╚═════╝  ╚═════╝ ╚═╝         ╚═╝     ╚═╝╚══════╝╚═╝     ╚═╝╚═════╝ ╚══════╝╚═╝  ╚═╝╚══════

    This application crawl clients groups and channels to add their members to the target group.
    Build: [repr.symbol]<VERSION> <PLATFORM> <BUILD_DATE>[/repr.symbol]
    Usage: 
        - Answer the questions.
        - [repr.symbol](Y/n)[/repr.symbol]: Y is default.
        - [repr.symbol](y/N)[/repr.symbol]: N is default.
    Copyright [repr.symbol](c) 2018 MJHP-ME[/repr.symbol]
"""
    get_console().print(
        Panel(
            Align.center(welcome_message),
            highlight=True,
            style="repr.success",
        )
    )
    get_console().print(
        Padding(Markdown(remarks_message), style="", pad=(0, 4, 0, 4)),
        highlight=True,
        style="repr.text",
    )
