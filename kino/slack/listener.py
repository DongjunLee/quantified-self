import json

import slack
import utils

class MsgListener(object):

    def __init__(self):
        self.config = utils.Config()
        self.router = slack.MsgRouter()
        self.slackbot = slack.SlackerAdapter()
        self.logger = utils.Logger().get_logger()

    def handle_message(self, msg):
        self.msg = json.loads(msg)
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
            self.router.route(text=self.msg['text'], user=self.msg['user'],
                              channel=self.msg['channel'], direct=self.__is__direct())
        except Exception as e:
            self.logger.error("USER Listener Error: ", e)
            self.slackbot.send_message(text=slack.MsgResource.ERROR)

    def handle_ifttt_message(self):
        try:
            self.router.route(text=self.__make_full_text(), direct=self.__is__direct(),
                              ifttt=True)
        except Exception as e:
            self.logger.error("IFTTT Listener Error: ", e)
            self.slackbot.send_message(text=slack.MsgResource.ERROR)

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
        if self.msg.get("subtype", None) == "bot_message":
            return True
        else:
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
        if text.startswith("<@"+ slack_bot_id + ">") or channel.startswith("D"):
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
            print(text)
            return text

    def __parse_attachments(self):
        pass


