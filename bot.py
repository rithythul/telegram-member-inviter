# pylint: disable=line-too-long
# pylint: disable=missing-module-docstring
import os
import sys
import time
import json
import socks

from rich.align import Align
from rich.highlighter import RegexHighlighter
from rich.theme import Theme
from rich.text import Text
from rich.console import Console
from rich.panel import Panel
from rich.padding import Padding
from rich.markdown import Markdown

# pylint: disable=unused-import
from telethon import TelegramClient, events, sync

# pylint: enable=unused-import
from telethon.tl import functions
from telethon.errors import ChatAdminRequiredError, FloodWaitError

CONFIGURATION_FILE_NAME = "clients.json"
CONFIGURATION_CLIENTS_SECTION_NAME = "clients"
CONFIGURATION_CLIENTS_SESSION_SECTION_NAME = "session_name"
CONFIGURATION_API_SECTION_NAME = "API"
CONFIGURATION_API_API_ID_SECTION_NAME = "API_ID"
CONFIGURATION_API_API_HASH_SECTION_NAME = "API_HASH"
CONFIGURATION_GROUP_SECTION_NAME = "group"
CONFIGURATION_PROXY_SECTION_NAME = "proxy"
CONFIGURATION_PROXY_PROTOCOL_NAME = "protocol"
CONFIGURATION_PROXY_HOST_NAME = "host"
CONFIGURATION_PROXY_PORT_NAME = "port"
CONFIGURATION_GROUP_INVITE_TO_THIS_GROUP_SECTION_NAME = "group_id_to_invite"
TELEGRAM_LIMITATION_TO_INVITE_USER_BY_CLIENT = 999


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


def print_banner():
    """Application Banner"""

    remarks_message = """
# Remarks:
1. Admin privileges or privilage to add member (in target group) is required for the client.
1. "A wait of n seconds is required (caused by InviteToChannelRequest)" is a known problem that caused by the limitation of the telegram for clients who act like a bot.
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


def main():
    """Main function."""

    data = {}
    data[CONFIGURATION_CLIENTS_SECTION_NAME] = []
    first_run = True
    want_to_add_more_client = True
    are_you_sure = False
    anythings_to_update = False
    want_to_use_proxy = False
    current_session_name = ""

    # You can set up as many clients as you want
    while True:
        if not first_run:
            want_to_add_more_client = (
                get_env(
                    "",
                    "Would you like to add more clients? (y/N): ",
                )
                == "y"
            )
        if not want_to_add_more_client:
            break
        if first_run:
            log(
                "warning",
                "If press (y), the old cached clients will be unreachable! \
                \n[INFO] If you already have the configured clients, press (n) to skip this step.",
            )
            are_you_sure = get_env("", "Do you want to configure clients? (y/N) ") == "y"
        if not are_you_sure:
            break
        current_session_name = get_env("", "Enter session name (<the_client_name>): ")
        data[CONFIGURATION_CLIENTS_SECTION_NAME].append(
            {CONFIGURATION_CLIENTS_SESSION_SECTION_NAME: current_session_name}
        )
        anythings_to_update = True
        if first_run:
            first_run = False

    # Retrieve the old session values if no new values have been set for the client session
    if not anythings_to_update:
        with open(
            CONFIGURATION_FILE_NAME, encoding="utf-8"
        ) as json_file:  # Get clients values from file
            data[CONFIGURATION_CLIENTS_SECTION_NAME] = json.load(json_file)[
                CONFIGURATION_CLIENTS_SECTION_NAME
            ]

    if (
        get_env(
            "",
            "Do you want to update API configurations? (y/N) ",
        )
        == "y"
    ):
        api_id = get_env("TG_API_ID", "Enter your API ID: ", int, is_password=True)
        api_hash = get_env("TG_API_HASH", "Enter your API hash: ", is_password=True)
        data[CONFIGURATION_API_SECTION_NAME] = {
            CONFIGURATION_API_API_ID_SECTION_NAME: api_id,
            CONFIGURATION_API_API_HASH_SECTION_NAME: api_hash,
        }
        anythings_to_update = True
    else:
        with open(
            CONFIGURATION_FILE_NAME, encoding="utf-8"
        ) as json_file:  # Get values from file
            data[CONFIGURATION_API_SECTION_NAME] = json.load(json_file)[
                CONFIGURATION_API_SECTION_NAME
            ]
            api_id = data[CONFIGURATION_API_SECTION_NAME][
                CONFIGURATION_API_API_ID_SECTION_NAME
            ]
            api_hash = data[CONFIGURATION_API_SECTION_NAME][
                CONFIGURATION_API_API_HASH_SECTION_NAME
            ]

    if (
        get_env(
            "",
            "Do you want to update the group ID (will be used to invite users into it)? (y/N) ",
        )
        == "y"
    ):
        group_id_to_invite = get_env(
            "",
            'Enter the "USERNAME" of the group you want to add members to it: ',
        )
        data[CONFIGURATION_GROUP_SECTION_NAME] = {
            CONFIGURATION_GROUP_INVITE_TO_THIS_GROUP_SECTION_NAME: group_id_to_invite
        }
        anythings_to_update = True
    else:
        with open(
            CONFIGURATION_FILE_NAME, encoding="utf-8"
        ) as json_file:  # Get values from file
            data[CONFIGURATION_GROUP_SECTION_NAME] = json.load(json_file)[
                CONFIGURATION_GROUP_SECTION_NAME
            ]
            group_id_to_invite = data[CONFIGURATION_GROUP_SECTION_NAME][
                CONFIGURATION_GROUP_INVITE_TO_THIS_GROUP_SECTION_NAME
            ]

    if get_env("", "Do you want to use proxy? (y/N) ") == "y":
        want_to_use_proxy = True
        use_old_proxy_settings = (
            get_env("", "Do you want to use old proxy settings? (y/N) ") == "y"
        )
        if not use_old_proxy_settings:
            if get_env("", "Enter the protocol? (HTTP/SOCKS5) ") == "HTTP":
                protocol = socks.HTTP
            else:
                protocol = socks.SOCKS5
            host = get_env("TG_PROXY_HOST", "Enter the host? ")
            port = get_env("TG_PROXY_PORT", "Enter the port? ", int)
            data[CONFIGURATION_PROXY_SECTION_NAME] = {
                CONFIGURATION_PROXY_HOST_NAME: host,
                CONFIGURATION_PROXY_PORT_NAME: port,
                CONFIGURATION_PROXY_PROTOCOL_NAME: protocol,
            }
        else:
            with open(
                CONFIGURATION_FILE_NAME, encoding="utf-8"
            ) as json_file:  # Get values from file
                data[CONFIGURATION_PROXY_SECTION_NAME] = json.load(json_file)[
                    CONFIGURATION_PROXY_SECTION_NAME
                ]
                host = data[CONFIGURATION_PROXY_SECTION_NAME][
                    CONFIGURATION_PROXY_HOST_NAME
                ]
                protocol = data[CONFIGURATION_PROXY_SECTION_NAME][
                    CONFIGURATION_PROXY_PROTOCOL_NAME
                ]
                port = data[CONFIGURATION_PROXY_SECTION_NAME][
                    CONFIGURATION_PROXY_PORT_NAME
                ]

    # Ensure that all values are updated
    with open(CONFIGURATION_FILE_NAME, encoding="utf-8", mode="w") as json_file:
        json.dump(data, json_file)

    clients = []
    for client in data[CONFIGURATION_CLIENTS_SECTION_NAME]:
        if want_to_use_proxy:
            clients.append(
                TelegramClient(
                    session=client[CONFIGURATION_CLIENTS_SESSION_SECTION_NAME],
                    api_id=api_id,
                    api_hash=api_hash,
                    proxy=(protocol, host, port),
                )
            )
        else:
            clients.append(
                TelegramClient(
                    session=client[CONFIGURATION_CLIENTS_SESSION_SECTION_NAME],
                    api_id=api_id,
                    api_hash=api_hash,
                )
            )

    def handler(client: TelegramClient):
        # Start client
        log("info", "Trying to start client")
        client.start()
        log("success", f'Successfully Logged in as "{client.session.filename}"')
        client_channels_or_groups_id = {}
        count_of_invited_user_by_this_client = 0
        # Fetching all the dialogs (conversations you have open)
        for dialog in client.iter_dialogs():
            if dialog.is_user:
                continue
            if not dialog.is_channel or not dialog.is_group:
                continue
            client_channels_or_groups_id[f"{dialog.name}:{dialog.id}"] = dialog.id

        log(
            "success",
            f'Successfully collected "{len(client_channels_or_groups_id)}" groups or channels to crawling their members',
        )
        for title, group_or_channel_id in client_channels_or_groups_id.items():
            # Check telegram limitation to invite users by each client
            if (
                count_of_invited_user_by_this_client
                > TELEGRAM_LIMITATION_TO_INVITE_USER_BY_CLIENT
            ):
                client.disconnect()
                log(
                    "info",
                    "Trying to change client because: telegram limitation for this client was applied",
                )
                break

            # Reset the array
            user_ids = (
                []
            )  # All user ids also channel creator ids except admins and bots
            participants = client.iter_participants(group_or_channel_id, 500)

            for participant in participants:
                if hasattr(participant, "admin_rights"):  # If user is admin
                    # then do not add it to array.
                    continue
                if participant.bot:
                    continue
                if participant.deleted:
                    continue
                user_ids.append(participant.id)
            channel_name = title.split(":")[0] or None
            log(
                "info",
                f'Trying to add "{len(user_ids)}" users to "{group_id_to_invite}" from "{channel_name}"',
            )
            action = get_env(
                "",
                f'Do you want to invite users from "{channel_name}" to "{group_id_to_invite}"? (Y/n) (s to skip this client) ',
            )
            if action == "n":
                continue
            if action == "s":
                break

            client_add_response = client(
                functions.channels.InviteToChannelRequest(
                    group_id_to_invite,
                    user_ids,
                )
            )
            log("info", f"{len(client_add_response.users)} users invited")
            count_of_invited_user_by_this_client += len(client_add_response.users)
        # Stop current client
        log("info", "Trying to stop client")
        client.disconnect()

    current_index = 0
    for client in clients:
        current_index = current_index + 1
        log("warning", f'Current session/client: "{client.session.filename}"')
        # In some cases, a client may wish to skip a session
        if get_env("", "Do you want to use this client? (Y/n) ") == "n":
            continue

        try:
            handler(client)
        except (ChatAdminRequiredError, FloodWaitError) as handler_err:
            log("error", f"{handler_err}")
            if current_index == len(clients):
                log("info", "No more client")
            else:
                log("info", "Trying to change client")
            client.disconnect()
            continue


if __name__ == "__main__":
    try:
        try:
            print_banner()
            main()
            get_env("", "Press Enter to exit ...")
        except KeyboardInterrupt:
            print("\n")
            log("info", "Goodbye ...")
    # pylint: disable=broad-except
    except Exception as main_err:
        # pylint: enable=broad-except
        log("error", f"{main_err}")
        get_env("", "Press Enter to exit ...")

    sys.exit(0)
