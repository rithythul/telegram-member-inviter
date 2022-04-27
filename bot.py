#!/usr/bin/env python3
# With this script, members of all clients will be added to the target group.
import os
import sys
import time
import json
import signal
import socks

from rich.align import Align
from rich.highlighter import RegexHighlighter
from rich.theme import Theme
from rich.text import Text
from rich.console import Console
from rich.panel import Panel
from rich.padding import Padding
from rich.markdown import Markdown

from telethon import TelegramClient, events, sync
from telethon.tl.functions.channels import GetParticipantsRequest
from telethon.tl.functions.channels import InviteToChannelRequest
from telethon.tl.types import ChannelParticipantsSearch

class GracefulInterruptHandler(object):
    """Handle key interupt

    CTRL+C
    """

    def __init__(self, sig=signal.SIGINT):
        self.sig = sig

    def __enter__(self):

        self.interrupted = False
        self.released = False

        self.original_handler = signal.getsignal(self.sig)

        def handler(signum, frame):
            self.release()
            self.interrupted = True

        signal.signal(self.sig, handler)

        return self

    def __exit__(self, type, value, tb):
        self.release()

    def release(self):

        if self.released:
            return False

        signal.signal(self.sig, self.original_handler)

        self.released = True

        return True


def get_env(name, message, cast=str, isPassword=False):
    console = get_console()
    if name in os.environ:
        return os.environ[name]
    while True:
        value = console.input(Text(message, style="repr.text"), password=isPassword)
        try:
            return cast(value)
        except ValueError as error:
            log('warning', 'Should be type of ' + str(cast.__name__) + '.')
            time.sleep(1)

def get_console():
    class Highlighter(RegexHighlighter):
        """Apply style to anything that looks like to my intentions."""

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

    theme = Theme({
        'repr.info': 'cyan',
        'repr.warning': 'yellow',
        'repr.error': 'bold red',
        'repr.success': 'green',
        'repr.text': 'grey63',
        'repr.command': 'cyan',
        'repr.symbol': 'gray62',
    })
    console = Console(highlighter=Highlighter(), theme=theme)
    return console

def log(type, message):
    def get_panel(type, message):
        return Panel('[' + type.upper() + '] ' + message, title=None, title_align="left", subtitle="↓", subtitle_align="left", border_style="repr.%s" % type, highlight=True, padding=1)

    get_console().print(get_panel(type, message))

def print_banner():
    """
    Application Banner
    """
    REMARKS = """ 
# Remarks:
1. Chat admin privileges are required to do that in the specified chat (for example, to send a message in a channel which is not yours).
1. "A wait of n seconds is required (caused by InviteToChannelRequest)" is a known problem that caused by the limitation of the telegram for clients who act like a bot.
1. You need to have the target group ID (It should be something similar to username).
"""
    WELCOME_MESSAGE = """
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
    Version: [repr.info]%s[/repr.info]
    Usage: - Please answer the questions!
           - Use CTRL+C to skip the client.
    Copyright [repr.info](c) 2018 MJHP-ME[/repr.info]
"""
    current_version = '1.1.6'
    get_console().print(Panel(Align.center(WELCOME_MESSAGE % current_version), highlight=True, style="repr.success"))
    get_console().print(Padding(Markdown(REMARKS), style="", pad=(0, 4, 0, 4)), highlight=True, style="repr.text")

def main():
    CONFIGURATION_FILE_NAME = 'clients.json'
    CONFIGURATION_CLIENTS_SECTION_NAME = 'clients'
    CONFIGURATION_CLIENTS_SESSION_SECTION_NAME = 'session_name'
    CONFIGURATION_API_SECTION_NAME = 'API'
    CONFIGURATION_API_API_ID_SECTION_NAME = 'API_ID'
    CONFIGURATION_API_API_HASH_SECTION_NAME = 'API_HASH'
    CONFIGURATION_GROUP_SECTION_NAME = 'group'
    CONFIGURATION_PROXY_SECTION_NAME = 'proxy'
    CONFIGURATION_PROXY_PROTOCOL_NAME = 'protocol'
    CONFIGURATION_PROXY_HOST_NAME = 'host'
    CONFIGURATION_PROXY_PORT_NAME = 'port'
    CONFIGURATION_GROUP_INVITE_TO_THIS_GROUP_SECTION_NAME = 'group_id_to_invite'
    TELEGRAM_LIMITATION_TO_INVITE_USER_BY_CLIENT = 999

    # Default limit and offset to get channel participants.
    offset = 0
    limit = 100

    data = {}  
    data[CONFIGURATION_CLIENTS_SECTION_NAME] = []  
    first_run = True
    want_to_add_more_client = True
    are_you_sure = False
    anythings_to_update = False
    want_to_use_proxy = False
    current_session_name = ''

    # You can set up as many clients as you want
    while True:
        if not first_run:
            want_to_add_more_client = get_env('TG_WANTED_TO_ADD_MORE_CLIENT', 'Would you like to add more clients? (y/N): ') == 'y'
        if not want_to_add_more_client:
            break
        if first_run:
            log('warning', 'If press (y), the old cached clients will be unreachable! \n[INFO] To skip this step, press (n) if you have already added clients and logged in with them.')
            are_you_sure = get_env('TG_ARE_YOU_SURE', 'Do you want to add client? (y/N) ') == 'y'
        if not are_you_sure:
            break
        current_session_name = get_env('TG_CURRENR_SESSION_NAME', 'Enter session name (<your_name>): ')
        data[CONFIGURATION_CLIENTS_SECTION_NAME].append({  
            CONFIGURATION_CLIENTS_SESSION_SECTION_NAME: current_session_name
        })
        anythings_to_update = True
        if first_run:
            first_run = False

    # Retrieve the old session values if no new values have been set for the client session
    if not anythings_to_update:
        with open(CONFIGURATION_FILE_NAME) as json_file: # Get clients values from file
            data[CONFIGURATION_CLIENTS_SECTION_NAME] = json.load(json_file)[CONFIGURATION_CLIENTS_SECTION_NAME]

    if get_env('TG_UPDATE_API_CONFIGURATIONS', 'Do you want to update API configurations? (y/N) ') == 'y':
        API_ID = get_env('TG_API_ID', 'Enter your API ID: ', int, isPassword=True)
        API_HASH = get_env('TG_API_HASH', 'Enter your API hash: ', isPassword=True)
        data[CONFIGURATION_API_SECTION_NAME] = {
            CONFIGURATION_API_API_ID_SECTION_NAME: API_ID,
            CONFIGURATION_API_API_HASH_SECTION_NAME: API_HASH
        }
        anythings_to_update = True
    else:
        with open(CONFIGURATION_FILE_NAME) as json_file: # Get values from file
            data[CONFIGURATION_API_SECTION_NAME] = json.load(json_file)[CONFIGURATION_API_SECTION_NAME]
            API_ID = data[CONFIGURATION_API_SECTION_NAME][CONFIGURATION_API_API_ID_SECTION_NAME]
            API_HASH = data[CONFIGURATION_API_SECTION_NAME][CONFIGURATION_API_API_HASH_SECTION_NAME]

    if get_env('TG_INVITE_GROUP_ID', 'Do you want to update the group ID (will be used to invite users to it)? (y/N) ') == 'y':
        INVITE_TO_THIS_GROUP_ID = get_env('TG_INVITE_GROUP_ID', 'Enter ID/USERNAME of group you want to add members to it: ')
        data[CONFIGURATION_GROUP_SECTION_NAME] = {
            CONFIGURATION_GROUP_INVITE_TO_THIS_GROUP_SECTION_NAME: INVITE_TO_THIS_GROUP_ID
        }
        anythings_to_update = True
    else:
        with open(CONFIGURATION_FILE_NAME) as json_file: # Get values from file
            data[CONFIGURATION_GROUP_SECTION_NAME] = json.load(json_file)[CONFIGURATION_GROUP_SECTION_NAME]
            INVITE_TO_THIS_GROUP_ID = data[CONFIGURATION_GROUP_SECTION_NAME][CONFIGURATION_GROUP_INVITE_TO_THIS_GROUP_SECTION_NAME]

    if get_env('TG_WANT_TO_USE_PROXY', 'Do you want to use proxy? (y/N) ') == 'y':
        want_to_use_proxy = True
        use_old_proxy_settings = get_env('TG_PROXY_USE_OLD', 'Do you want to use old proxy settings? (y/N) ') == 'y'
        if not use_old_proxy_settings:
            if get_env('TG_PROXY_PROTOCOL', 'Enter the protocol? (HTTP/SOCKS5) ') == 'HTTP':
                protocol = socks.HTTP
            else:
                protocol = socks.SOCKS5
            host = get_env('TG_PROXY_HOST', 'Enter the host? ')
            port = get_env('TG_PROXY_PORT', 'Enter the port? ', int)
            data[CONFIGURATION_PROXY_SECTION_NAME] = {
                CONFIGURATION_PROXY_HOST_NAME: host,
                CONFIGURATION_PROXY_PORT_NAME: port,
                CONFIGURATION_PROXY_PROTOCOL_NAME: protocol
            }
        else:
            with open(CONFIGURATION_FILE_NAME) as json_file: # Get values from file
                data[CONFIGURATION_PROXY_SECTION_NAME] = json.load(json_file)[CONFIGURATION_PROXY_SECTION_NAME]
                host = data[CONFIGURATION_PROXY_SECTION_NAME][CONFIGURATION_PROXY_HOST_NAME]
                protocol = data[CONFIGURATION_PROXY_SECTION_NAME][CONFIGURATION_PROXY_PROTOCOL_NAME]
                port = data[CONFIGURATION_PROXY_SECTION_NAME][CONFIGURATION_PROXY_PORT_NAME]

    # Ensure that all values are updated
    with open(CONFIGURATION_FILE_NAME, 'w') as json_file:        
        json.dump(data, json_file)

    clients = []
    for client in data[CONFIGURATION_CLIENTS_SECTION_NAME]:
        if want_to_use_proxy:
            clients.append(TelegramClient(
                session=client[CONFIGURATION_CLIENTS_SESSION_SECTION_NAME],
                api_id=API_ID, 
                api_hash=API_HASH,
                proxy=(protocol, host, port)
            ))
        else:
            clients.append(TelegramClient(
                session=client[CONFIGURATION_CLIENTS_SESSION_SECTION_NAME],
                api_id=API_ID, 
                api_hash=API_HASH
            ))

    for client in clients:
        log('info', 'Current session: %s' % (client.session.filename))
        # In some cases, a client may wish to skip a session
        if get_env('TG_WANT_TO_USE_THIS_CLIENT', 'Do you want to use this client? (Y/n) ') == 'n':
            continue
        else:
            # Start client
            log('info', 'Trying to start client')
            client.start()
            log('success', 'Successfuly Logged in as: %s' % (client.session.filename))
        client_channels_or_groups_id = []
        count_of_invited_user_by_this_client = 0
        # Fetching all the dialogs (conversations you have open)
        for dialog in client.get_dialogs():
            if dialog.is_user:
                continue
            if not dialog.is_channel:
                continue
            if not dialog.is_group:
                continue
            client_channels_or_groups_id.append(dialog.id)

        with GracefulInterruptHandler() as interrupt_handler:
            for client_or_channel_id in client_channels_or_groups_id:
                if interrupt_handler.interrupted:
                    log('info', 'Trying to change client')
                    # Stop current client
                    log('info', 'Trying to stop client')
                    client.disconnect()
                    break
                # Depricated. reset user array in each itteration
                all_users_id_also_channel_creator_id_except_admins_and_bots = []
                # Check telegram limitation to inive users by each client
                if count_of_invited_user_by_this_client > TELEGRAM_LIMITATION_TO_INVITE_USER_BY_CLIENT:
                    log('info', 'Trying to stop client')
                    client.disconnect()
                    log('info', 'Trying to change client because: telegram limitation for this client was applied')
                    break
                        

                # Collect all users except admins into the array.
                while True:
                    if interrupt_handler.interrupted:
                        log('info', 'Trying to change client')
                        # Stop current client
                        log('info', 'Trying to stop client')
                        client.disconnect()
                        break
                    # Check telegram limitation to inive users by each client
                    if count_of_invited_user_by_this_client > TELEGRAM_LIMITATION_TO_INVITE_USER_BY_CLIENT:
                        break
                    # Reset the array
                    all_users_id_also_channel_creator_id_except_admins_and_bots = []
                    participants = client(GetParticipantsRequest(
                        client_or_channel_id, ChannelParticipantsSearch(''), offset, limit, hash=0
                    ))
                    if not participants.participants: # All users was fetched
                        break
                    for participant in participants.participants:
                        if hasattr(participant, 'admin_rights'): # If user was admin 
                                                                # then do not add it to array.
                            continue
                        # Add specific user into the array where user id was equal to the
                        # participant.user_id.
                        for user in participants.users:
                            if user.id == participant.user_id:
                                # Remove finded user from users list for better performance
                                participants.users.remove(user)
                                # If user was bot the remove it from list and continue
                                if user.bot:
                                    break
                                if user.deleted:
                                    break
                                # Add finded user to the array
                                all_users_id_also_channel_creator_id_except_admins_and_bots.append(user.id)
                                break
                            # Continue to search in array to find user
                            continue
                    offset += len(participants.participants)
                    # Add users to the channel
                    log('info', 'Try to add %d users' % len(all_users_id_also_channel_creator_id_except_admins_and_bots))
                    client_add_response = client(InviteToChannelRequest(INVITE_TO_THIS_GROUP_ID, all_users_id_also_channel_creator_id_except_admins_and_bots))
                    log('success', '%d users invited' % len(client_add_response.users))
                    count_of_invited_user_by_this_client += len(client_add_response.users)
                    # Check telegram limitation to inive users by each client
                    if count_of_invited_user_by_this_client > TELEGRAM_LIMITATION_TO_INVITE_USER_BY_CLIENT:
                        break
            # Stop current client
            log('info', 'Trying to stop client')
            client.disconnect()


if __name__ == '__main__':
    try:
        print_banner()
        try:
            main()
        except Exception as e:
            log('error', '%s' % e)
    except KeyboardInterrupt as k:
        print("\n")
        log('info', 'Bye :)')
        sys.exit(0)
