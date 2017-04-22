# coding: UTF-8

import asyncio
import time
import websockets

import slack
from slack import MsgResource
import utils

# Send a message to channel (init)
slackbot = slack.SlackerAdapter()

logger = utils.Logger().get_logger()

# load skill data
utils.SkillData()

config = utils.Config()
MASTER_NAME = config.bot["MASTER_NAME"]
BOT_NAME = config.bot["BOT_NAME"]
slackbot.send_message(text=MsgResource.HELLO(MASTER_NAME, BOT_NAME))

def start_session(nap=False):
    try:
        # Start RTM
        endpoint = slackbot.start_real_time_messaging_session()
        listener = slack.MsgListener()
        logger.info('start real time messaging session!')

        if nap:
            slackbot.send_message(text=MsgResource.NAP)

        async def execute_bot():
            ws = await websockets.connect(endpoint)
            while True:
                receive_json = await ws.recv()
                listener.handle(receive_json)

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        asyncio.get_event_loop().run_until_complete(execute_bot())
        asyncio.get_event_loop().run_forever()
    except Exception as e:
        logger.error("Session Error. restart in 5 minutes..")
        logger.error(repr(e))
        time.sleep(5 * 60)
        start_session(nap=True)


start_session()
