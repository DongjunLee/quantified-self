# -*- coding: utf-8 -*-

import datetime

from functions.functions import Functions
from slack.slackbot import SlackerAdapter
from slack.template import MsgTemplate

class FunctionManager(object):

    def __init__(self):
        self.slackbot = SlackerAdapter()
        self.functions = Functions().registered
        self.template = MsgTemplate()

    def execute(self, func_name):
        pass

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
        self.slackbot.send_message(text="사용할 수 있는 Function 리스트 입니다.", attachments=attachments)
