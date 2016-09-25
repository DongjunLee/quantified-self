#coding: UTF-8

import asyncio
import os
import websockets

from slacker import Slacker

from slack.listener import SlackListener

SLACK_TOKEN = os.environ["KINO_BOT_TOKEN"]
slack = Slacker(SLACK_TOKEN)

# Send a message to channel (init)
slack.chat.post_message(channel='#bot_test',
                        text='Stalker Bot Start!',
                        as_user=True)

# Start Bot
response = slack.rtm.start()
endpoint = response.body['url']

async def execute_bot():
    ws = await websockets.connect(endpoint)
    listener = SlackListener()
    while True:
        message_json = await ws.recv()
        listener.handle_only_message(message_json)

loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)
asyncio.get_event_loop().run_until_complete(execute_bot())
asyncio.get_event_loop().run_forever()
