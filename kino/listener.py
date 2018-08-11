import json

from hbconfig import Config

from .route import MsgRouter

from .slack.resource import MsgResource
from .slack.slackbot import SlackerAdapter

from .utils.logger import Logger


class MsgListener(object):
    def __init__(self) -> None:
        self.router = MsgRouter()
        self.slackbot = SlackerAdapter()
        self.logger = Logger().get_logger()

    def handle(self, msg: str) -> None:
        self.msg = json.loads(msg)
        self.handle_message()
        self.handle_presence_change()
        self.handle_dnd_change()

    def handle_message(self) -> MsgRouter.message_route:
        if self.is_message():
            is_bot = self.is_bot()
            if not self.is_self() and not is_bot:
                self.handle_user_message()
            elif is_bot and self.is_webhook():
                self.handle_webhook_message()
        else:
            pass

    def handle_user_message(self) -> MsgRouter.message_route:
        try:
            self.router.message_route(
                text=self.msg["text"],
                user=self.msg["user"],
                channel=self.msg["channel"],
                direct=self.is_direct(),
            )
        except Exception as e:
            self.logger.error(f"USER Listener Error: {e}")
            self.logger.exception("user")
            self.slackbot.send_message(text=MsgResource.ERROR)

    def handle_webhook_message(self) -> MsgRouter.message_route:
        try:
            self.router.message_route(
                text=self.make_full_text(), direct=self.is_direct(), webhook=True
            )
        except Exception as e:
            self.logger.error(f"Webhook Listener Error: {e}")
            self.logger.exception("webhook")
            self.slackbot.send_message(text=MsgResource.ERROR)

    def is_message(self, msg=None) -> bool:
        if msg is None:
            msg = self.msg

        msg_type = msg.get("type", None)
        if msg_type == "message":
            return True
        else:
            return False

    def is_self(self, msg=None) -> bool:
        if msg is None:
            msg = self.msg

        if msg.get("user", None) == self.slackbot.get_bot_id():
            return True
        else:
            return False

    def is_bot(self, msg=None) -> bool:
        if msg is None:
            msg = self.msg

        if "bot_id" in msg:
            return True

        subtype = msg.get("subtype", None)
        if subtype == "bot_message":
            return True
        if subtype == "message_changed":
            message = msg.get("message", None)
            if "bot_id" in message:
                return True

        return False

    def is_webhook(self, msg=None) -> bool:
        if msg is None:
            msg = self.msg

        if (
            msg.get("username", None) == "IFTTT"
            or self.msg.get("username", None) == "incoming-webhook"
        ):
            return True
        else:
            return False

    def is_direct(self, msg=None) -> bool:
        if msg is None:
            msg = self.msg

        text = msg.get("text", "$#")
        channel = msg.get("channel", "")
        slack_bot_id = self.slackbot.get_bot_id()
        if (
            f"<@{slack_bot_id}>" in text
            or channel.startswith("D")
            or any(
                [
                    text.lower().startswith(t.lower())
                    for t in Config.bot.get("TRIGGER", ["키노야", "Hey kino"])
                ]
            )
        ):
            return True
        else:
            return False

    def make_full_text(self) -> str:
        if self.msg.get("text", None):
            return self.msg["text"]
        else:
            text = ""
            for attachment in self.msg["attachments"]:
                text += attachment["text"]
            return text

    def parse_attachments(self):
        pass

    def handle_presence_change(self) -> MsgRouter.presence_route:
        if self.is_presence() and not self.is_self():
            try:
                self.router.presence_route(
                    user=self.msg["user"], presence=self.msg["presence"]
                )
            except Exception as e:
                self.logger.error(f"Presence Listener Error: {e}")
                self.logger.exception("presence")
                self.slackbot.send_message(text=MsgResource.ERROR)

    def is_presence(self, msg=None) -> bool:
        if msg is None:
            msg = self.msg

        msg_type = msg.get("type", None)
        if msg_type == "presence_change":
            return True
        else:
            return False

    def handle_dnd_change(self) -> MsgRouter.dnd_route:
        if self.is_dnd_updated_user() and not self.is_self():
            try:
                self.router.dnd_route(dnd=self.msg["dnd_status"])
            except Exception as e:
                self.logger.error(f"dnd_change Listener Error: {e}")
                self.logger.exception("dnd")
                self.slackbot.send_message(text=MsgResource.ERROR)

    def is_dnd_updated_user(self, msg=None) -> bool:
        if msg is None:
            msg = self.msg

        msg_type = msg.get("type", None)
        if msg_type == "dnd_updated_user":
            return True
        else:
            return False

    # TODO : user_change  ex) 'status_text': 'In a meeting'
