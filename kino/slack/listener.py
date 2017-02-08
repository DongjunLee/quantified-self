import json

import slack
import utils

class MsgListener(object):

    def __init__(self):
        self.config = utils.Config()
        self.router = slack.MsgRouter()
        self.slackbot = slack.SlackerAdapter()
        self.logger = utils.Logger().get_logger()

    def handle_only_message(self, msg):
        self.msg = json.loads(msg)

        msg_type = self.msg.get("type", None)
        if msg_type == "message" and not self.__is_self():
            try:
                self.router.route(text=self.msg['text'], user=self.msg['user'])
            except Exception as e:
                self.logger.error("Listener Error: ", e)
                self.slackbot.send_message(text=slack.MsgResource.ERROR)

    def handle_only_direct_message(self, msg):
        self.msg = json.loads(msg)

        if (self.__is_message() and not self.__is_self() and self.__is__direct()):
            try:
                self.router.route(text=self.msg['text'], user=self.msg['user'], channel=self.msg['channel'])
            except Exception as e:
                self.logger.error("Listener Error: ", e)
                self.slackbot.send_message(text=slack.MsgResource.ERROR)

    def __is_message(self):
        msg_type = self.msg.get("type", None)
        if msg_type == "message":
            return True
        else:
            return False

    def __is_self(self):
        if self.msg["user"] == self.slackbot.get_bot_id():
            return True
        else:
            return False

    def __is__direct(self):
        text = self.msg.get("text", "")
        channel = self.msg.get("channel", "")
        slack_bot_id = self.slackbot.get_bot_id()
        if text.startswith("<@"+ slack_bot_id + ">") or channel.startswith("D"):
            return True
        else:
            return False

    def __make_full_text(self):
        pass

    def __parse_attachments(self):
        pass


