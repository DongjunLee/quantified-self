# coding: UTF-8

import asyncio
import time
import websockets

from .listener import MsgListener

from .slack.resource import MsgResource
from .slack.slackbot import SlackerAdapter

from .utils.config import Config
from .utils.logger import Logger
from .utils.data_loader import SkillData


class KinoBot(object):

    def __init__(self):
        self.slackbot = SlackerAdapter()
        self.logger = Logger().get_logger()

        # load skill data
        SkillData()

        # Send a message to channel (init)
        config = Config()
        MASTER_NAME = config.bot["MASTER_NAME"]
        BOT_NAME = config.bot["BOT_NAME"]
        self.slackbot.send_message(text=MsgResource.HELLO(master_name=MASTER_NAME, bot_name=BOT_NAME))

    def start_session(self, nap=False):
        try:
            # Start RTM
            endpoint = self.slackbot.start_real_time_messaging_session()
            listener = MsgListener()
            self.logger.info('start real time messaging session!')

            if nap:
                self.slackbot.send_message(text=MsgResource.NAP)

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
            self.logger.error("Session Error. restart in 5 minutes..")
            self.logger.exception("bot")
            time.sleep(5 * 60)
            self.start_session(nap=True)
