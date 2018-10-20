from telethon import TelegramClient, events, sync
import socks

# These example values won't work. You must get your own api_id and
# api_hash from https://my.telegram.org, under API Development. test 2 group id:-1001296960728
api_id = 396542
api_hash = '185a7473e0c34763fa43eec8f77fee5f'

# clientNMK = TelegramClient('majid_account2',
#     api_id=396542, api_hash='185a7473e0c34763fa43eec8f77fee5f',
#     proxy=(socks.SOCKS5, 'localhost', 9050)
# )
# clientNMK.start()

clientH = TelegramClient('majid_account1',
    api_id=396542, api_hash='185a7473e0c34763fa43eec8f77fee5f',
    proxy=(socks.SOCKS5, 'localhost', 9050)
)
clientH.start()

# clientElmGosar = TelegramClient('majid_account3',
#     api_id=396542, api_hash='185a7473e0c34763fa43eec8f77fee5f',
#     proxy=(socks.SOCKS5, 'localhost', 9050)
# )
# clientElmGosar.start()

# clientKeshavarzOnline = TelegramClient('majid_account4',
#     api_id=396542, api_hash='185a7473e0c34763fa43eec8f77fee5f',
#     proxy=(socks.SOCKS5, 'localhost', 9050)
# )
# clientKeshavarzOnline.start()

# clientKeshavarzii = TelegramClient('majid_account5',
#     api_id=396542, api_hash='185a7473e0c34763fa43eec8f77fee5f',
#     proxy=(socks.SOCKS5, 'localhost', 9050)
# )
# clientKeshavarzii.start()

# clientK = TelegramClient('majid_account6',
#     api_id=396542, api_hash='185a7473e0c34763fa43eec8f77fee5f',
#     proxy=(socks.SOCKS5, 'localhost', 9050)
# )
# clientK.start()

# clientAgri = TelegramClient('majid_account7',
#     api_id=396542, api_hash='185a7473e0c34763fa43eec8f77fee5f',
#     proxy=(socks.SOCKS5, 'localhost', 9050)
# )
# clientAgri.start()

# groupTestForElmGostar = clientElmGosar.get_entity('https://t.me/joinchat/A5MctUZjaWGlBcZibXA7SQ')
groupTestForH = clientH.get_entity('https://t.me/joinchat/A5MctUZjaWGlBcZibXA7SQ')
# groupTestForNMK = clientNMK.get_entity('https://t.me/joinchat/A5MctUZjaWGlBcZibXA7SQ')

# groupTest2ForElmGostar = clientElmGosar.get_entity('https://t.me/joinchat/A5MctQ7qVzBqn-VaYxjdBQ')
groupTest2ForH = clientH.get_entity('https://t.me/joinchat/A5MctQ7qVzBqn-VaYxjdBQ')
# groupTest2ForNMK = clientNMK.get_entity('https://t.me/joinchat/A5MctQ7qVzBqn-VaYxjdBQ')

# Send message to into the test grou
# clientElmGosar.send_message(groupTestForElmGostar, 'سلام. از طرف ان ام کا!')
# clientH.send_message(groupTestForH, 'سلام. از طرف اچ!')
# clientNMK.send_message(groupTestForNMK, 'سلام. از طرف علم گستر!')

# from telethon.tl.functions.channels import InviteToChannelRequest

from telethon.tl.functions.users import GetFullUserRequest

users = []
# Try to add users to group test2
for user in clientH.get_participants(groupTestForH, aggressive=True):
    if user.bot:
        continue
    users.append(user.id)

# clientH(InviteToChannelRequest('https://t.me/joinchat/A5MctQ7qVzBqn-VaYxjdBQ', users))

from telethon.tl.functions.channels import GetParticipantsRequest
from telethon.tl.types import ChannelParticipantsSearch
from time import sleep

offset = 0
limit = 100
all_admins_except_creator = []

while True:
    participants = clientH(GetParticipantsRequest(
        'https://t.me/joinchat/A5MctQ7qVzBqn-VaYxjdBQ', ChannelParticipantsSearch(''), offset, limit, hash=0
    ))
    if not participants.participants:
        break
    for participant in participants.participants:
        if not hasattr(participant, 'admin_rights'):
            continue
        # Remove other user (users who was not admin)
        all_admins_except_creator.append(participant)
    offset += len(participants.participants)

# text_file = open("users.txt", "w")

# for user in client.get_participants(fromGroupOrChannel):
#     if user.bot:
#         text_file.write("---------------> ")
#     text_file.write("user id: %d, " % user.id)
#     text_file.write("user username: %s, \n" % user.username)

# text_file.close()

# Retrieving messages from a chat
# from telethon import utils
# for message in client.iter_messages('Der_letzte_mensch', limit=10):
#     print(utils.get_display_name(message.sender), message.message)

# Listing all the dialogs (conversations you have open)
# for dialog in client.get_dialogs(limit=1):
#     print(dialog.name, dialog.draft.text)

# Downloading profile photos (default path is the working directory)
# client.download_profile_photo('Der_letzte_mensch')

from telethon import events

# Get sender message informations
# @client.on(events.NewMessage)
# async def handler(event):
#     print((await event.get_sender()).stringify())

# @client.on(events.NewMessage(incoming=True, pattern='(?i)hi'))
# async def handler(event):
#     await event.reply('Hello!')

# client.run_until_disconnected()
