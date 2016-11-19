# -*- coding: utf-8 -*-

import datetime
import json
import schedule

import functions
import slack
import utils

class FunctionManager(object):

    def __init__(self, text=None):
        self.input = text
        self.slackbot = slack.SlackerAdapter()
        self.functions = functions.Functions().registered
        self.template = slack.MsgTemplate()
        self.logger = utils.Logger().get_logger()

    def load_function(self, start_time=None, end_time=None,
                      func_name=None, params=None, repeat=False):

        self.logger.info("load_function: " + str(func_name) + ", " + str(params))

        if not repeat:
            self.__excute(func_name, params)
            return schedule.CancelJob
        elif (repeat) and (self.__is_between(start_time, end_time)):
            self.__excute(func_name, params)

    def __excute(self, func_name, params):
        getattr(functions.Functions(), func_name)(**params)

    def __is_between(self, start_time, end_time):
        now = datetime.datetime.now()

        start_h, start_m = start_time
        end_h, end_m = end_time

        if end_h == 24 and end_m == 0:
            end_h = 23; end_m = 59

        start = now.replace(hour=start_h, minute=start_m, second=0, microsecond=0)
        end = now.replace(hour=end_h, minute=end_m, second=0, microsecond=0)
        if (start < now < end):
            return True
        else:
            return False

    def read(self):
        attachments = self.template.make_function_template("", self.functions)
        self.slackbot.send_message(attachments=attachments)
