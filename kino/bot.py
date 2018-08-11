import asyncio
import time
import websockets

from hbconfig import Config

from .listener import MsgListener

from .slack.resource import MsgResource
from .slack.slackbot import SlackerAdapter
from .slack.slackbot import GiphyClient

from .utils.logger import Logger


class KinoBot:
    def __init__(self) -> None:
        self.slackbot = SlackerAdapter()
        self.logger = Logger().get_logger()

        # Send a message to channel (init)
        MASTER_NAME = Config.bot.MASTER_NAME
        BOT_NAME = Config.bot.BOT_NAME
        self.slackbot.send_message(
            text=MsgResource.HELLO(master_name=MASTER_NAME, bot_name=BOT_NAME)
        )

        giphy = GiphyClient()
        giphy.search("Hello!")

        self.error_delay = 5

    def start_session(self, nap: bool = False):
        try:
            # Start RTM
            endpoint = self.slackbot.start_real_time_messaging_session()
            listener = MsgListener()
            self.logger.info("start real time messaging session!")

            async def execute_bot():
                ws = await websockets.connect(endpoint)
                while True:
                    receive_json = await ws.recv()
                    listener.handle(receive_json)

            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            asyncio.get_event_loop().run_until_complete(execute_bot())
            asyncio.get_event_loop().run_forever()

            if nap:
                self.slackbot.send_message(text=MsgResource.NAP)

        except BaseException:
            self.slackbot.send_message(text=MsgResource.SESSION_ERROR)

            self.logger.error("Session Error. restart in 5 seconds..")
            self.logger.exception("bot")
            time.sleep(5)
            self.start_session(nap=True)

            if self.error_delay <= 1000:
                self.error_delay *= 2
