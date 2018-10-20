#!/usr/bin/env python3
# A simple script invite members from all clients groups into the target group
import os
import sys
import time
import json
import socks

from telethon import TelegramClient, events, sync
from telethon.tl.functions.channels import GetParticipantsRequest
from telethon.tl.functions.channels import InviteToChannelRequest
from telethon.tl.types import ChannelParticipantsSearch


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
CONFIGURATION_CLIENTS_SECTION_NAME = 'clients'
CONFIGURATION_CLIENTS_SESSION_SECTION_NAME = 'session_name'
CONFIGURATION_API_SECTION_NAME = 'API'
CONFIGURATION_API_API_ID_SECTION_NAME = 'API_ID'
CONFIGURATION_API_API_HASH_SECTION_NAME = 'API_HASH'
CONFIGURATION_GROUP_SECTION_NAME = 'group'
CONFIGURATION_GROUP_INVITE_TO_THIS_GROUP_SECTION_NAME = 'group_id_to_invite'

# Default limit and offset to get participants of channel 
offset = 0
limit = 9999

data = {}  
data[CONFIGURATION_CLIENTS_SECTION_NAME] = []  
first_run = True
want_to_add_more_client = True
are_you_sure = False
update_old_sessions = False
anythings_to_update = False
want_to_use_proxy = False
current_session_name = ''

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
    if get_env('TG_PROXY_PROTOCOL', 'What is you protocol? (HTTP/SOCKS5) ') == 'HTTP':
        protocol = socks.HTTP
    else:
        protocol = socks.SOCKS5
    host = get_env('TG_PROXY_HOST', 'Enter your host? ')
    port = get_env('TG_PROXY_PORT', 'Enter your port? ', int)

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
    print('Current Session Was: %s' % (client.session.filename))
    client.start()
    client_channels_or_groups_id = []
    # Fetching all the dialogs (conversations you have open)
    for dialog in client.get_dialogs():
        if dialog.is_user:
            continue
        if not dialog.is_channel:
            continue
        if not dialog.is_group:
            continue
        client_channels_or_groups_id.append(dialog.id)

    for client_or_channel_id in client_channels_or_groups_id:
        all_users_id_also_channel_creator_id_except_admins_and_bots = []

        # Collect all users except admins into the array.
        while True:
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
                        # Add finded user to the array
                        all_users_id_also_channel_creator_id_except_admins_and_bots.append(user.id)
                        break
                    # Other users was skipped
                    continue
            offset += len(participants.participants)

        # Add users to the channel
        client(InviteToChannelRequest(INVITE_TO_THIS_GROUP_ID, all_users_id_also_channel_creator_id_except_admins_and_bots))
