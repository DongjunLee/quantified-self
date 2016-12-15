import json

import slack
import utils

class MsgListener(object):

    def __init__(self):
        self.router = slack.MsgRouter()
        self.slackbot = slack.SlackerAdapter()
        self.logger = utils.Logger().get_logger()

    def handle_only_message(self, msg):
        self.msg = json.loads(msg)

        msg_type = self.msg.get("type", None)
        if msg_type == "message" and not self.__is_self_message():
            try:
                self.router.route(text=self.msg['text'], user=self.msg['user'])
            except Exception as e:
                self.logger.error("Listener Error: ", e)
                self.slackbot.send_message(text=slack.MsgResource.ERROR)

    def __is_self_message(self):
        if self.msg["user"] == self.slackbot.get_bot_id():
            return True
        else:
            return False

    def __make_full_text(self):
        pass

    def __parse_attachments(self):
        pass


