# -*- coding: utf-8 -*-

import datetime
import json

from functions.functions import Functions
from slack.slackbot import SlackerAdapter
from slack.template import MsgTemplate

class FunctionManager(object):

    def __init__(self):
        self.slackbot = SlackerAdapter()
        self.functions = Functions().registered
        self.template = MsgTemplate()

    def load_function(self, start_time=None, end_time=None, func_name=None, params=None):

        if self.__is_between(start_time, end_time):
            functions = Functions()
            params = json.loads(params)
            getattr(functions, func_name)(**params)

    def __is_between(self, start_time, end_time):
        now = datetime.datetime.now()

        start_h, start_m = start_time
        end_h, end_m = end_time

        start = now.replace(hour=start_h, minute=start_m, second=0, microsecond=0)
        end = now.replace(hour=end_h, minute=end_m, second=0, microsecond=0)
        if (start < now < end):
            return True
        else:
            return False

    def read(self):
        attachments = self.template.make_function_template("", self.functions)
        self.slackbot.send_message(attachments=attachments)
