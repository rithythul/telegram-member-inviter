# pylint: disable=line-too-long
# pylint: disable=missing-module-docstring
import json

import socks
# pylint: disable=unused-import
from telethon import TelegramClient
from telethon.errors import ChatAdminRequiredError, FloodWaitError
# pylint: enable=unused-import
from telethon.tl import functions

from .util import get_env, log

__CONFIG_FILE_NAME = "clients.json"
__CONFIG_CLIENTS_SECTION_NAME = "clients"
__CONFIG_CLIENTS_SESSION_SECTION_NAME = "session_name"
__CONFIG_API_SECTION_NAME = "API"
__CONFIG_API_API_ID_SECTION_NAME = "API_ID"
__CONFIG_API_API_HASH_SECTION_NAME = "API_HASH"
__CONFIG_GROUP_SECTION_NAME = "group"
__CONFIG_PROXY_SECTION_NAME = "proxy"
__CONFIG_PROXY_PROTOCOL_NAME = "protocol"
__CONFIG_PROXY_HOST_NAME = "host"
__CONFIG_PROXY_PORT_NAME = "port"
__CONFIG_GROUP_INVITE_TO_THIS_GROUP_SECTION_NAME = "group_id_to_invite"
__TELEGRAM_LIMIT = 999


def load_config(key):
    with open(__CONFIG_FILE_NAME, 'r', encoding='utf-8') as file:
        data = json.load(file)
        return data[key]


def save_config(data):
    with open(__CONFIG_FILE_NAME, 'w', encoding='utf-8') as file:
        json.dump(data, file)


def is_yes(prompt):
    answer = get_env("", prompt + ' (y/N) ')
    return answer == 'y' or answer == 'Y'


def is_no(prompt):
    answer = get_env("", prompt + " (Y/n) ")
    return answer == 'n' or answer == 'N'


def loop():
    """Main function."""

    data = {__CONFIG_CLIENTS_SECTION_NAME: []}
    first_run = True
    want_to_add_more_client = True
    are_you_sure = False
    anythings_to_update = False
    want_to_use_proxy = False

    # You can set up as many clients as you want
    while True:
        if not first_run:
            want_to_add_more_client = is_yes("Would you like to add more clients?")
        if not want_to_add_more_client:
            break
        if first_run:
            log(
                "warning",
                "If press (y), the old cached clients will be unreachable! \
                \n[INFO] If you already have the configured clients, press (n) to skip this step.",
            )
            are_you_sure = is_yes("Do you want to configure clients?")
        if not are_you_sure:
            break
        current_session_name = get_env("", "Enter session name (<the_client_name>): ")
        data[__CONFIG_CLIENTS_SECTION_NAME].append(
            {__CONFIG_CLIENTS_SESSION_SECTION_NAME: current_session_name}
        )
        anythings_to_update = True
        if first_run:
            first_run = False

    # Retrieve the old session values if no new values have been set for the client session
    if not anythings_to_update:
        data[__CONFIG_CLIENTS_SECTION_NAME] = load_config(__CONFIG_CLIENTS_SECTION_NAME)

    if is_yes("Do you want to update API configurations?"):
        api_id = get_env("TG_API_ID", "Enter your API ID: ", int, is_password=True)
        api_hash = get_env("TG_API_HASH", "Enter your API hash: ", is_password=True)
        data[__CONFIG_API_SECTION_NAME] = {
            __CONFIG_API_API_ID_SECTION_NAME: api_id,
            __CONFIG_API_API_HASH_SECTION_NAME: api_hash,
        }
    else:
        pass

    data[__CONFIG_API_SECTION_NAME] = load_config(__CONFIG_API_SECTION_NAME)
    api_id = data[__CONFIG_API_SECTION_NAME][
        __CONFIG_API_API_ID_SECTION_NAME
    ]
    api_hash = data[__CONFIG_API_SECTION_NAME][
        __CONFIG_API_API_HASH_SECTION_NAME
    ]

    if is_yes("Do you want to update the group ID (will be used to invite users into it)?"):
        group_id_to_invite = get_env(
            "",
            'Enter the "USERNAME" of the group you want to add members to it: ',
        )
        data[__CONFIG_GROUP_SECTION_NAME] = {
            __CONFIG_GROUP_INVITE_TO_THIS_GROUP_SECTION_NAME: group_id_to_invite
        }
    else:
        data[__CONFIG_GROUP_SECTION_NAME] = load_config(__CONFIG_GROUP_SECTION_NAME)
        group_id_to_invite = data[__CONFIG_GROUP_SECTION_NAME][
            __CONFIG_GROUP_INVITE_TO_THIS_GROUP_SECTION_NAME
        ]

    if is_yes("Do you want to use proxy?"):
        want_to_use_proxy = True
        use_old_proxy_settings = is_yes("Do you want to use old proxy settings?")
        if not use_old_proxy_settings:
            if get_env("", "Enter the protocol? (HTTP/SOCKS5) ") == "HTTP":
                protocol = socks.HTTP
            else:
                protocol = socks.SOCKS5
            host = get_env("TG_PROXY_HOST", "Enter the host? ")
            port = get_env("TG_PROXY_PORT", "Enter the port? ", int)
            data[__CONFIG_PROXY_SECTION_NAME] = {
                __CONFIG_PROXY_HOST_NAME: host,
                __CONFIG_PROXY_PORT_NAME: port,
                __CONFIG_PROXY_PROTOCOL_NAME: protocol,
            }
        else:
            data[__CONFIG_PROXY_SECTION_NAME] = load_config(__CONFIG_PROXY_SECTION_NAME)
            host = data[__CONFIG_PROXY_SECTION_NAME][
                __CONFIG_PROXY_HOST_NAME
            ]
            protocol = data[__CONFIG_PROXY_SECTION_NAME][
                __CONFIG_PROXY_PROTOCOL_NAME
            ]
            port = data[__CONFIG_PROXY_SECTION_NAME][
                __CONFIG_PROXY_PORT_NAME
            ]

    # Ensure that all values are updated
    save_config(data)

    clients = []
    for client in data[__CONFIG_CLIENTS_SECTION_NAME]:
        if want_to_use_proxy:
            clients.append(
                TelegramClient(
                    session=client[__CONFIG_CLIENTS_SESSION_SECTION_NAME],
                    api_id=api_id,
                    api_hash=api_hash,
                    proxy=(protocol, host, port),
                )
            )
        else:
            clients.append(
                TelegramClient(
                    session=client[__CONFIG_CLIENTS_SESSION_SECTION_NAME],
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
                    > __TELEGRAM_LIMIT
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
        if is_no("Do you want to use this client?"):
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


def cli():
    loop()
    get_env("", "Press Enter to exit ...")
