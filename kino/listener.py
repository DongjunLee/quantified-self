import json

from .route import MsgRouter

from .slack.resource import MsgResource
from .slack.slackbot import SlackerAdapter

from .utils.config import Config
from .utils.logger import Logger


class MsgListener(object):

    def __init__(self):
        self.config = Config()
        self.router = MsgRouter()
        self.slackbot = SlackerAdapter()
        self.logger = Logger().get_logger()

    def handle(self, msg):
        self.msg = json.loads(msg)
        self.handle_message()
        self.handle_presence_change()
        self.handle_dnd_change()

    def handle_message(self):
        if self.__is_message():
            is_bot = self.__is_bot()
            if not self.__is_self() and not is_bot:
                self.handle_user_message()
            elif is_bot and self.__is_ifttt():
                self.handle_ifttt_message()
        else:
            pass

    def handle_user_message(self):
        try:
            self.router.route(
                text=self.msg['text'],
                user=self.msg['user'],
                channel=self.msg['channel'],
                direct=self.__is__direct())
        except Exception as e:
            self.logger.error(f"USER Listener Error: {e}")
            self.logger.exception("user")
            self.slackbot.send_message(text=MsgResource.ERROR)

    def handle_ifttt_message(self):
        try:
            self.router.route(
                text=self.__make_full_text(),
                direct=self.__is__direct(),
                ifttt=True)
        except Exception as e:
            self.logger.error(f"IFTTT Listener Error: {e}")
            self.logger.exception("ifttt")
            self.slackbot.send_message(text=MsgResource.ERROR)

    def __is_message(self):
        msg_type = self.msg.get("type", None)
        if msg_type == "message":
            return True
        else:
            return False

    def __is_self(self):
        if self.msg.get("user", None) == self.slackbot.get_bot_id():
            return True
        else:
            return False

    def __is_bot(self):
        if "bot_id" in self.msg:
            return True

        subtype = self.msg.get("subtype", None)
        if subtype == "bot_message":
            return True
        if subtype == "message_changed":
            message = self.msg.get("message", None)
            if "bot_id" in message:
                return True

        return False

    def __is_ifttt(self):
        if self.msg.get("username", None) == "IFTTT":
            return True
        else:
            return False

    def __is__direct(self):
        text = self.msg.get("text", "")
        channel = self.msg.get("channel", "")
        slack_bot_id = self.slackbot.get_bot_id()
        if text.startswith(
            "<@" +
            slack_bot_id +
                ">") or channel.startswith("D"):
            return True
        else:
            return False

    def __make_full_text(self):
        if self.msg.get("text", None):
            return slef.msg["text"]
        else:
            text = ""
            for attachment in self.msg["attachments"]:
                text += attachment["text"]
            return text

    def __parse_attachments(self):
        pass

    def handle_presence_change(self):
        if self.__is_presence() and not self.__is_self():
            try:
                self.router.route(presence=self.msg['presence'])
            except Exception as e:
                self.logger.error(f"Presence Listener Error: {e}")
                self.logger.exception("presence")
                self.slackbot.send_message(text=MsgResource.ERROR)

    def __is_presence(self):
        msg_type = self.msg.get("type", None)
        if msg_type == "presence_change":
            return True
        else:
            return False

    def handle_dnd_change(self):
        if self.__is_dnd_updated_user() and not self.__is_self():
            try:
                dnd = self.msg['dnd_status']
                self.router.route(dnd=dnd['dnd_enabled'])
            except Exception as e:
                self.logger.error(f"dnd_change Listener Error: {e}")
                self.logger.exception("dnd")
                self.slackbot.send_message(text=MsgResource.ERROR)

    def __is_dnd_updated_user(self):
        msg_type = self.msg.get("type", None)
        if msg_type == "dnd_updated_user":
            return True
        else:
            return False
