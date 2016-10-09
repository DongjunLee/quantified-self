#coding: UTF-8

import asyncio
import websockets
from utils.config import Config

from slack.slackbot import SlackerAdapter
from kino.listener import MsgListener

# Send a message to channel (init)
slackbot = SlackerAdapter()

config = Config()
MASTER_NAME = config.kino["MASTER_NAME"]
BOT_NAME = config.kino["BOT_NAME"]
hello_text = "{}님 안녕하세요! \n저는 {}님의 개인비서 {}입니다.\n반갑습니다.".format(MASTER_NAME, MASTER_NAME, BOT_NAME)
slackbot.send_message(text=hello_text)

# Start RTM
endpoint = slackbot.start_real_time_messaging_session()
listener = MsgListener()

async def execute_bot():
    ws = await websockets.connect(endpoint)
    while True:
        message_json = await ws.recv()
        listener.handle_only_message(message_json)

loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)
asyncio.get_event_loop().run_until_complete(execute_bot())
asyncio.get_event_loop().run_forever()
