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

# Initialize config data
defaults = {
    "api": {
        "id": "default_id",
        "hash": "default_hash"
    }
}


def loop():
    """Main function."""

    data = {CONFIGURATION_CLIENTS_SECTION_NAME: []}
    first_run = True
    want_to_add_more_client = True
    are_you_sure = False
    anythings_to_update = False
    want_to_use_proxy = False

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
            are_you_sure = (
                get_env("", "Do you want to configure clients? (y/N) ") == "y"
            )
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


def cli():
    loop()
    get_env("", "Press Enter to exit ...")
