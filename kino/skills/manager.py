# -*- coding: utf-8 -*-

import json
import schedule

import skills
import slack
import utils

class FunctionManager(object):

    def __init__(self, text=None):
        self.input = text
        self.slackbot = slack.SlackerAdapter()
        self.functions = skills.Functions().registered
        self.template = slack.MsgTemplate()
        self.logger = utils.Logger().get_logger()

    def load_function(self, start_time=None, end_time=None,
                      func_name=None, params=None, repeat=False, holiday=False):

        if holiday == False and skills.Summary().is_holiday() == True:
            return

        if not repeat:
            self.__excute(func_name, params)
            return schedule.CancelJob
        elif (repeat) and (utils.ArrowUtil().is_between(start_time, end_time)):
            self.__excute(func_name, params)

    def __excute(self, func_name, params):
        self.logger.info("load_function: " + str(func_name) + ", " + str(params))
        getattr(skills.Functions(), func_name)(**params)

    def read(self):
        attachments = self.template.make_skill_template("", self.functions)
        self.slackbot.send_message(attachments=attachments)
