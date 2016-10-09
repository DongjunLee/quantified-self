import json

from kino.route import MsgRouter
from slack.slackbot import SlackerAdapter

class MsgListener(object):

    def __init__(self):
        self.router = MsgRouter()
        self.slackbot = SlackerAdapter()

    def handle_only_message(self, msg):
        self.msg = json.loads(msg)

        msg_type = self.msg.get("type", None)
        if msg_type == "message" and not self.__is_self_message():
            self.router.route(text=self.msg['text'], user=self.msg['user'])

    def __is_self_message(self):
        if self.msg["user"] == self.slackbot.get_bot_id():
            return True
        else:
            return False

    def __make_full_text(self):
        pass

    def __parse_attachments(self):
        pass


