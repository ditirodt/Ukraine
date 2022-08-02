"""
  This is a class that scrape messages from telegram channel

"""
import configparser
import json
import asyncio
from datetime import date, datetime

from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError
from telethon.tl.functions.messages import (GetHistoryRequest)
from telethon.tl.types import (
    PeerChannel
)



class DateTimeEncoder(json.JSONEncoder):
    """
    function to parse json date

    """
    def default(self, o):
        if isinstance(o, datetime):
            return o.isoformat()

        if isinstance(o, bytes):
            return list(o)

        return json.JSONEncoder.default(self, o)


"""
    Read Configs i.e API credential which are in the config.in file for security purposes

"""
config = configparser.ConfigParser()
config.read("config.ini")

# Setting configuration values
api_id = config['Telegram']['api_id']
api_hash = config['Telegram']['api_hash']

api_hash = str(api_hash)

phone = config['Telegram']['phone']
username = config['Telegram']['username']


"""
    Create the client and connect

"""

client = TelegramClient(username, api_id, api_hash)


async def main(phone):
    """
    This a main method to start the client and connect to the telegram channel

    It ensures that the client is authorized and then it will get the messages from the channel, the phone number is suppossed to be in full i.e country code + phone number

    """
    await client.start()
    print("Client Created")
    # Ensure you're authorized
    if await client.is_user_authorized() == False:
        await client.send_code_request(phone)
        try:
            await client.sign_in(phone, input('Enter the code: '))
        except SessionPasswordNeededError:
            await client.sign_in(password=input('Password: '))

    me = await client.get_me()

    user_input_channel = input('Please enter the URL of the channel:')

    if user_input_channel.isdigit():
        entity = PeerChannel(int(user_input_channel))
    else:
        entity = user_input_channel

    my_channel = await client.get_entity(entity)

    offset_id = 0
    limit = 100
    all_messages = []
    total_messages = 0
    total_count_limit = 0

    while True:
        print("Current Offset ID is:", offset_id, "; Total Messages:", total_messages)
        history = await client(GetHistoryRequest(
            peer=my_channel,
            offset_id=offset_id,
            offset_date=None,
            add_offset=0,
            limit=limit,
            max_id=0,
            min_id=0,
            hash=0
        ))
        if not history.messages:
            print('There are no messages in this channel')
            break
        messages = history.messages
        for message in messages:
            if "university" or "scholarship" in messages:
                all_messages.append(message.to_dict())
                offset_id = messages[len(messages) - 1].id
                total_messages = len(all_messages)
                if total_count_limit != 0 and total_messages >= total_count_limit:
                    break
                print("messages found")
            else:
                print("no education message found!")

    with open('channel_messages.json', 'w') as outfile:
        json.dump(all_messages, outfile, cls=DateTimeEncoder)


with client:
    client.loop.run_until_complete(main(phone))
