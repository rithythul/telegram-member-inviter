from telethon import TelegramClient, events, sync
import socks

api_id = 396542
api_hash = '185a7473e0c34763fa43eec8f77fee5f'

# clientNMK = TelegramClient('majid_account2',
#     api_id=396542, api_hash='185a7473e0c34763fa43eec8f77fee5f',
#     proxy=(socks.SOCKS5, 'localhost', 9050)
# )
# clientNMK.start()

client_h = TelegramClient('majid_account1',
    api_id=396542, api_hash='185a7473e0c34763fa43eec8f77fee5f',
    proxy=(socks.SOCKS5, 'localhost', 9050)
)
client_h.start()

# client_elm_gosar = TelegramClient('majid_account3',
#     api_id=396542, api_hash='185a7473e0c34763fa43eec8f77fee5f',
#     proxy=(socks.SOCKS5, 'localhost', 9050)
# )
# client_elm_gosar.start()

# client_keshavarz_online = TelegramClient('majid_account4',
#     api_id=396542, api_hash='185a7473e0c34763fa43eec8f77fee5f',
#     proxy=(socks.SOCKS5, 'localhost', 9050)
# )
# client_keshavarz_online.start()

# client_keshavarzii = TelegramClient('majid_account5',
#     api_id=396542, api_hash='185a7473e0c34763fa43eec8f77fee5f',
#     proxy=(socks.SOCKS5, 'localhost', 9050)
# )
# client_keshavarzii.start()

# client_k = TelegramClient('majid_account6',
#     api_id=396542, api_hash='185a7473e0c34763fa43eec8f77fee5f',
#     proxy=(socks.SOCKS5, 'localhost', 9050)
# )
# client_k.start()

# client_agri = TelegramClient('majid_account7',
#     api_id=396542, api_hash='185a7473e0c34763fa43eec8f77fee5f',
#     proxy=(socks.SOCKS5, 'localhost', 9050)
# )
# client_agri.start()

# group_test_for_elm_gostar = clientElmGosar.get_entity('https://t.me/joinchat/A5MctUZjaWGlBcZibXA7SQ')
group_test_for_h = client_h.get_entity('https://t.me/joinchat/A5MctUZjaWGlBcZibXA7SQ')
# group_test_for_nmk = clientNMK.get_entity('https://t.me/joinchat/A5MctUZjaWGlBcZibXA7SQ')

# group_test2_for_elm_gostar = clientElmGosar.get_entity('https://t.me/joinchat/A5MctQ7qVzBqn-VaYxjdBQ')
group_test2_for_h = client_h.get_entity('https://t.me/joinchat/A5MctQ7qVzBqn-VaYxjdBQ')
# group_test2_for_nmk = clientNMK.get_entity('https://t.me/joinchat/A5MctQ7qVzBqn-VaYxjdBQ')

client_h_channels = []
# Fetching all the dialogs (conversations you have open)
for dialog in client_h.get_dialogs():
    if dialog.is_user:
        continue
    if not dialog.is_channel:
        continue
    if not dialog.is_group:
        continue
    client_h_channels.append(dialog.id)

from telethon.tl.functions.channels import GetParticipantsRequest
from telethon.tl.types import ChannelParticipantsSearch

offset = 0
limit = 100
all_users_id_also_channel_creator_id_except_admins_and_bots = []

# Collect all users except admins into the array.
while True:
    participants = client_h(GetParticipantsRequest(
        -1001180920161, ChannelParticipantsSearch(''), offset, limit, hash=0
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

from telethon.tl.functions.channels import InviteToChannelRequest

# all_users_id_also_channel_creator_id_except_admins_and_bots = ['Der_letzte_mensch']
# Add users to the channel test2
client_h(InviteToChannelRequest(-1001296960728, all_users_id_also_channel_creator_id_except_admins_and_bots))
