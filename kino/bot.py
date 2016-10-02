#coding: UTF-8

import asyncio
import websockets

from slack.slackbot import SlackerAdapter
from slack.listener import SlackListener

# Send a message to channel (init)
slackbot = SlackerAdapter()
slackbot.send_message(text='동준님 안녕하세요! \n저는 동준님의 개인비서 Kino입니다.\n반갑습니다.')

# Start RTM
endpoint = slackbot.start_real_time_messaging_session()

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
