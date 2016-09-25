# -*- coding: utf-8 -*-

import datetime
import os

from slacker import Slacker

from slack.template import MsgTemplate

class FunctionTable(object):

    def __init__(self):
        SLACK_TOKEN = os.environ["KINO_BOT_TOKEN"]
        self.slacker = Slacker(SLACK_TOKEN)
        self.functions = self.__load_functions()
        self.template = MsgTemplate()

    def __load_functions(self):
        function_list = []

        send_message = {}
        send_message["name"] = "send_message"
        send_message["detail"] = {
            "name": "send_message",
            "params": ["text"],
            "description": "#bot_test 채널로 메시지를 전송합니다."
        }

        function_list.append(send_message)

        return function_list

    def send_message(params):

        def function(text="input_text"):
            self.slacker.chat.post_message(channel="#bot_test",
                                            text=text,
                                            as_user=True)

        detail = {
            "name": "send_message",
            "params": ["text"],
            "description": "#bot_test 채널로 메시지를 전송합니다."
        }

        func = {"call": function(**params), "detail": detail}
        return func

    def __is_between(self, start_time=(7,0), end_time=(24,0)):
        now = datetime.datetime.now()
        now_6pm = now.replace(hour=start_time[0], minute=start_time[1], second=0, microsecond=0)
        now_11pm = now.replace(hour=end_time[0], minute=end_time[1], second=0, microsecond=0)
        if (now_6pm < now < now_11pm):
            return True
        else:
            return False

    def read(self, params):
        attachments = self.template.make_function_template("", self.functions)
        self.slacker.chat.post_message(channel="#bot_test", text="Function List.",
                                       attachments=attachments, as_user=True)

