#coding: UTF-8

import asyncio
import websockets

import slack
import utils

# Send a message to channel (init)
slackbot = slack.SlackerAdapter()

config = utils.Config()
MASTER_NAME = config.bot["MASTER_NAME"]
BOT_NAME = config.bot["BOT_NAME"]
hello_text = "{}님 안녕하세요! \n저는 개인비서 {} 라고 합니다.\n반갑습니다.".format(MASTER_NAME, BOT_NAME)
slackbot.send_message(text=hello_text)

# Start RTM
endpoint = slackbot.start_real_time_messaging_session()
listener = slack.MsgListener()

logger = utils.Logger().get_logger()
logger.info('start real time messaging session!')

def start_session():
    async def execute_bot():
        ws = await websockets.connect(endpoint)
        while True:
            message_json = await ws.recv()
            listener.handle_only_message(message_json)

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    asyncio.get_event_loop().run_until_complete(execute_bot())
    asyncio.get_event_loop().run_forever()

try:
    start_session()
except Exception as e:
    logger.error("Session Error: ", e)
    start_session()
