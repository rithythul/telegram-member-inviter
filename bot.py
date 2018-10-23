#!/usr/bin/env python3
# A simple script invite members from all clients groups into the target group
import os
import sys
import time
import json
import socks
import signal

from telethon import TelegramClient, events, sync
from telethon.tl.functions.channels import GetParticipantsRequest
from telethon.tl.functions.channels import InviteToChannelRequest
from telethon.tl.types import ChannelParticipantsSearch

# Capture SIGINT in Python
class GracefulInterruptHandler(object):

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


def get_env(name, message, cast=str):
    if name in os.environ:
        return os.environ[name]
    while True:
        value = input(message)
        try:
            return cast(value)
        except ValueError as e:
            print(e, file=sys.stderr)
            time.sleep(1)


CONFIGURATION_FILE_NAME = 'clients.json'
VERSION_FILE_NAME = 'version.json'
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

# Default limit and offset to get participants of channel 
offset = 0
limit = 100

data = {}  
data[CONFIGURATION_CLIENTS_SECTION_NAME] = []  
first_run = True
want_to_add_more_client = True
are_you_sure = False
update_old_sessions = False
anythings_to_update = False
want_to_use_proxy = False
current_session_name = ''

# APPLICATION WELCOME MESSAGE
with open(VERSION_FILE_NAME) as version_file: # Get clients values from file
    WELCOME_MESSAGE = """ 
    This application used to add members of clients group into the terget group.
    Version: %s
    Python Version: 3.6.6
    Usage: - Just answer the questions.
            - To skip client when trying to add members just use CTRL+C
    Copyright MJHP-ME 2018
    """
    current_version = json.load(version_file)['version']
    print(WELCOME_MESSAGE % current_version)

# Get as many as clients you want
while True:
    if not first_run:
        want_to_add_more_client = get_env('TG_WANTED_TO_ADD_MORE_CLIENT', 'Do you want to still add more clients(y/n): ') == 'y'
    if not want_to_add_more_client:
        break
    if first_run:
        print('Add more clients. the old one was removed, then if you want to use old sessions please skip this step.')
        are_you_sure = get_env('TG_ARE_YOU_SURE', 'Are you sure? (y/n) ') == 'y'
    if not are_you_sure:
        break
    current_session_name = get_env('TG_CURRENR_SESSION_NAME', 'Enter session name (<your_name>): ')
    data[CONFIGURATION_CLIENTS_SECTION_NAME].append({  
        CONFIGURATION_CLIENTS_SESSION_SECTION_NAME: current_session_name
    })
    anythings_to_update = True
    if first_run:
        first_run = False

# Get clients session from old values if not new values was set
if not anythings_to_update:
    with open(CONFIGURATION_FILE_NAME) as json_file: # Get clients values from file
        data[CONFIGURATION_CLIENTS_SECTION_NAME] = json.load(json_file)[CONFIGURATION_CLIENTS_SECTION_NAME]

if get_env('TG_UPDATE_API_CONFIGURATIONS', 'Want to update APIs configurations? (y/n) ') == 'y':
    API_ID = get_env('TG_API_ID', 'Enter your API ID: ', int)
    API_HASH = get_env('TG_API_HASH', 'Enter your API hash: ')
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

if get_env('TG_INVITE_GROUP_ID', 'Want to update group ID to invite users to it? (y/n) ') == 'y':
    INVITE_TO_THIS_GROUP_ID = get_env('TG_INVITE_GROUP_ID', 'Enter ID of group you want to add members to it: ', int)
    data[CONFIGURATION_GROUP_SECTION_NAME] = {
        CONFIGURATION_GROUP_INVITE_TO_THIS_GROUP_SECTION_NAME: INVITE_TO_THIS_GROUP_ID
    }
    anythings_to_update = True
else:
    with open(CONFIGURATION_FILE_NAME) as json_file: # Get values from file
        data[CONFIGURATION_GROUP_SECTION_NAME] = json.load(json_file)[CONFIGURATION_GROUP_SECTION_NAME]
        INVITE_TO_THIS_GROUP_ID = data[CONFIGURATION_GROUP_SECTION_NAME][CONFIGURATION_GROUP_INVITE_TO_THIS_GROUP_SECTION_NAME]

if get_env('TG_WANT_TO_USE_PROXY', 'Do you want to use proxy? (y/n) ') == 'y':
    want_to_use_proxy = True
    use_old_proxy_settings = get_env('TG_PROXY_USE_OLD', 'Want to use old proxy settings? (y/n) ') == 'y'
    if not use_old_proxy_settings:
        if get_env('TG_PROXY_PROTOCOL', 'What is you protocol? (HTTP/SOCKS5) ') == 'HTTP':
            protocol = socks.HTTP
        else:
            protocol = socks.SOCKS5
        host = get_env('TG_PROXY_HOST', 'Enter your host? ')
        port = get_env('TG_PROXY_PORT', 'Enter your port? ', int)
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

# Make sure to update all values
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
    print('----> Current session: %s' % (client.session.filename))
    # Maybe some of the clients want to skip
    if get_env('TG_WANT_TO_USE_THIS_CLIENT', 'Do you want to use this client? (y/n) ') == 'n':
        continue
    else:
        # Start client
        print('----> Trying to start client')
        client.start()
        print('----> Successfuly Logged in as: %s' % (client.session.filename))
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

    with GracefulInterruptHandler() as h:
        for client_or_channel_id in client_channels_or_groups_id:
            if h.interrupted:
                print("----> Trying to change client")
                # Stop current client
                print('----> Trying to stop client')
                client.disconnect()
                break
            # Depricated. reset user array in each itteration
            all_users_id_also_channel_creator_id_except_admins_and_bots = []
            # Check telegram limitation to inive users by each client
            if count_of_invited_user_by_this_client > TELEGRAM_LIMITATION_TO_INVITE_USER_BY_CLIENT:
                print('----> Trying to stop client')
                client.disconnect()
                print('----> Trying to change client because: telegram limitation for this client was applied')
                break
                    

            # Collect all users except admins into the array.
            while True:
                if h.interrupted:
                    print("----> Trying to change client")
                    # Stop current client
                    print('----> Trying to stop client')
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
                print('Try to add %d users' % len(all_users_id_also_channel_creator_id_except_admins_and_bots))
                client_add_response = client(InviteToChannelRequest(INVITE_TO_THIS_GROUP_ID, all_users_id_also_channel_creator_id_except_admins_and_bots))
                print('%d users invited' % len(client_add_response.users))
                count_of_invited_user_by_this_client += len(client_add_response.users)
                # Check telegram limitation to inive users by each client
                if count_of_invited_user_by_this_client > TELEGRAM_LIMITATION_TO_INVITE_USER_BY_CLIENT:
                    break
        # Stop current client
        print('----> Trying to stop client')
        client.disconnect()