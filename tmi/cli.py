# pylint: disable=line-too-long
# pylint: disable=missing-module-docstring
import dataclasses
import json
import os
from typing import Tuple

import socks
# pylint: disable=unused-import
from telethon import TelegramClient
from telethon.errors import ChatAdminRequiredError, FloodWaitError
# pylint: enable=unused-import
from telethon.tl import functions

from .util import get_env, log

__CONFIG_FILE_NAME = "clients.json"
__TELEGRAM_LIMIT = 999


def load_config() -> "ConfigStruct":
    """
    The structure of config is:
     {
         "clients": [
             {"session_name": String}
         ],
         "api": {"api_id": Int, "api_hash": String},
         "group": {"group_id_to_invite": String},
         "proxy": {"host": String, "port": Int, "protocol": Int}
    }
    """
    if not os.path.exists(__CONFIG_FILE_NAME):
        log("warning", f'No config file found in path: "./{__CONFIG_FILE_NAME}"')
        return ConfigStruct(
            clients=[],
            api=ApiConfig(),
            group=GroupConfig()
        )
    with open(__CONFIG_FILE_NAME, 'r', encoding='utf-8') as file:
        data = json.load(file)
        return ConfigStruct(
            clients=data["clients"],
            api=data["api"],
            group=data["group"],
            proxy=data["proxy"]
        )


def save_config(data):
    with open(__CONFIG_FILE_NAME, 'w', encoding='utf-8') as file:
        json.dump(data, file)


def is_yes(prompt):
    answer = get_env("", prompt + ' (y/N) ')
    return answer == 'y' or answer == 'Y'


def is_no(prompt):
    answer = get_env("", prompt + " (Y/n) ")
    return answer == 'n' or answer == 'N'


def invite_members_to_target_group(config: "ConfigStruct", clients: "ClientGenerator"):
    """Main function."""

    def handler(t_client: TelegramClient):
        # Start client
        log("info", "Trying to start client")
        t_client.start()
        log("success", f'Successfully Logged in as "{t_client.session.filename}"')
        client_channels_or_groups_id = {}
        count_of_invited_user_by_this_client = 0
        # Fetching all the dialogs (conversations you have open)
        for dialog in t_client.iter_dialogs():
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
                t_client.disconnect()
                log(
                    "info",
                    "Trying to change client because: telegram limitation for this client was applied",
                )
                break

            # Reset the array
            user_ids = (
                []
            )  # All user ids also channel creator ids except admins and bots
            participants = t_client.iter_participants(group_or_channel_id, 500)

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
                f'Trying to add "{len(user_ids)}" users to "{config.group.group_id_to_invite}" from "{channel_name}"',
            )
            action = get_env(
                "",
                f'Do you want to invite users from "{channel_name}" to "{config.group.group_id_to_invite}"? (Y/n) (s to skip this client) ',
            )
            if action == "n":
                continue
            if action == "s":
                break

            client_add_response = t_client(
                functions.channels.InviteToChannelRequest(
                    config.group.group_id_to_invite,
                    user_ids,
                )
            )
            log("info", f"{len(client_add_response.users)} users invited")
            count_of_invited_user_by_this_client += len(client_add_response.users)
        # Stop current client
        log("info", "Trying to stop client")
        t_client.disconnect()

    for client in clients:
        log("warning", f'Current session/client: "{client.session.filename}"')
        # In some cases, a client may wish to skip a session
        if is_no("Do you want to use this client?"):
            continue

        try:
            handler(client)
        except (ChatAdminRequiredError, FloodWaitError) as handler_err:
            client.disconnect()
            log("error", f"{handler_err}")
            if is_yes("Do you want to change client?"):
                continue


def init_context() -> Tuple["Context", "ConfigStruct"]:
    _context = Context()
    _config = load_config()

    while True:
        if not _context.first_run:
            if is_no("Would you like to add more clients?"):
                break
        if _context.first_run:
            log(
                "warning",
                "If press (y), the old cached clients will be unreachable! \
                \n[INFO] If you already have the configured clients, press (n) to skip this step.",
            )
            if is_no("Do you want to configure clients?"):
                break
        current_session_name = get_env("", "Enter session name (<the_client_name>): ")
        _config.clients.append(ClientConfig(session_name=current_session_name))
        if _context.first_run:
            _context.first_run = False

    if is_yes("Do you want to update api configurations?"):
        api_id = get_env("TG_API_ID", "Enter your api id: ", int, is_password=True)
        api_hash = get_env("TG_API_HASH", "Enter your api hash: ", is_password=True)
        _config.api = ApiConfig(api_id, api_hash)

    if is_yes("Do you want to update the group ID (will be used to invite users into it)?"):
        group_id_to_invite = get_env(
            "",
            'Enter the "USERNAME" of the group you want to add members to it: ',
        )
        _config.group = GroupConfig(group_id_to_invite)

    if is_yes("Do you want to use proxy?"):
        _context.want_to_use_proxy = True
        use_old_proxy_settings = is_yes("Do you want to use old proxy settings?")
        if not use_old_proxy_settings:
            if get_env("", "Enter the protocol? (HTTP/SOCKS5) ") == "HTTP":
                protocol = socks.HTTP
            else:
                protocol = socks.SOCKS5
            host = get_env("TG_PROXY_HOST", "Enter the host? ")
            port = get_env("TG_PROXY_PORT", "Enter the port? ", int)
            _config.proxy = ProxyConfig(host, port, protocol)

    # TODO: Observer pattern to update json file on each changes
    return _context, _config


def cli() -> None:
    """
    The CLI for the Telegram Member Inviter (TMI).
    """
    context, config = init_context()
    client_generator = ClientGenerator(config, context)
    invite_members_to_target_group(config=config, clients=client_generator)
    get_env("", "Press Enter to exit ...")


class ClientGenerator:
    def __init__(self, config: "ConfigStruct", context: "Context") -> None:
        self._config = config
        self._context = context
        self._client_counts = len(config.clients)

    def __iter__(self):
        return self

    def __next__(self):
        if not self._config.clients:
            raise StopIteration

        client = self._config.clients.pop()
        params = {
            "session": client.session_name,
            "api_id": self._config.api.api_id,
            "api_hash": self._config.api.api_hash,
        }
        if self._context.want_to_use_proxy:
            params["proxy"] = (self._config.proxy.protocol, self._config.proxy.host, self._config.proxy.port)
        return TelegramClient(**params)


@dataclasses.dataclass
class ClientConfig:
    session_name: str


@dataclasses.dataclass
class ApiConfig:
    api_id: int
    api_hash: str


@dataclasses.dataclass
class GroupConfig:
    group_id_to_invite: str


@dataclasses.dataclass
class ProxyConfig:
    host: str
    port: int
    protocol: int


@dataclasses.dataclass
class ConfigStruct:
    clients: list[ClientConfig]
    api: ApiConfig
    group: GroupConfig
    proxy: ProxyConfig | None = None


@dataclasses.dataclass
class Context:
    first_run: bool = True
    want_to_use_proxy: bool = False
