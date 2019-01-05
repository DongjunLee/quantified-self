import asyncio
import time
import websockets

from hbconfig import Config

from kino.bot.worker import Worker
from kino.listener import MsgListener

from kino.slack.resource import MsgResource
from kino.slack.slackbot import SlackerAdapter
from kino.slack.slackbot import GiphyClient

from kino.utils.logger import Logger


class KinoBot:
    def __init__(self) -> None:
        self.slackbot = SlackerAdapter()
        self.logger = Logger().get_logger()
        self.worker = Worker(slackbot=self.slackbot)

        self.error_delay = 1  # Unit (Second)

        # Send a message to channel (init)
        MASTER_NAME = Config.bot.MASTER_NAME
        BOT_NAME = Config.bot.BOT_NAME
        self.slackbot.send_message(
            text=MsgResource.HELLO(master_name=MASTER_NAME, bot_name=BOT_NAME)
        )

        giphy = GiphyClient()
        giphy.search("Hello!")


    def start_session(self, init: bool = False, nap: bool = False):
        self.worker.stop(init=init)
        self.worker.run(init=init)

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
            self.logger.error(f"Session Error. restart in {self.error_delay} seconds..")
            self.logger.exception("bot")
            time.sleep(5)
            self.start_session(nap=True)

            if self.error_delay <= 1000:
                self.error_delay *= 2
