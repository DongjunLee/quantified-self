# -*- coding: utf-8 -*-

import random

from ..slack.resource import MsgResource
from ..slack.slackbot import SlackerAdapter
from ..slack.template import MsgTemplate

from ..utils.data_handler import DataHandler
from ..utils.state import State


class Between(object):

    def __init__(self, text=None, slackbot=None):
        self.input = text
        self.data_handler = DataHandler()
        self.fname = "schedule.json"
        self.template = MsgTemplate()

        if slackbot is None:
            self.slackbot = SlackerAdapter()
        else:
            self.slackbot = slackbot

    def create(self, step=0, params=None):
        state = State()

        def step_0(params):
            self.slackbot.send_message(text=MsgResource.BETWEEN_CREATE_START)
            self.data_handler.read_json_then_add_data(
                self.fname, "between", {})
            state.flow_start("Between", "create")

            self.slackbot.send_message(text=MsgResource.BETWEEN_CREATE_STEP1)

        def step_1(params):
            b_index, current_between_data = self.data_handler.get_current_data(
                self.fname, "between")
            current_between_data['time_interval'] = params
            self.data_handler.read_json_then_edit_data(
                self.fname, "between", b_index, current_between_data)

            state.flow_next_step()
            self.slackbot.send_message(text=MsgResource.BETWEEN_CREATE_STEP2)

        def step_2(params):
            b_index, current_between_data = self.data_handler.get_current_data(
                self.fname, "between")
            current_between_data['color'] = self.__generate_color_code()
            current_between_data['description'] = params
            self.data_handler.read_json_then_edit_data(
                self.fname, "between", b_index, current_between_data)

            state.flow_complete()
            self.slackbot.send_message(text=MsgResource.CREATE)

        locals()["step_" + str(step)](params)

    def __generate_color_code(self):
        def r(): return random.randint(0, 255)
        color_code = '#%02X%02X%02X' % (r(), r(), r())
        return color_code

    def read(self):
        attachments = self.__make_between_list()
        if attachments is None:
            self.slackbot.send_message(text=MsgResource.EMPTY)
            return "empty"
        else:
            self.slackbot.send_message(attachments=attachments)
            return "success"

    def __make_between_list(self):
        schedule_data = self.data_handler.read_file(self.fname)
        between_data = schedule_data.get('between', {})

        if between_data == {} or len(between_data) == 1:
            return None
        else:
            return self.template.make_schedule_template("", between_data)

    def update(self, step=0, params=None):
        b_index, input_time_interval, input_description = params[0].split(
            " + ")
        input_between = {
            "time_interval": input_time_interval,
            "description": input_description}

        result = self.data_handler.read_json_then_edit_data(
            self.fname, "between", b_index, input_between)

        if result == "sucess":
            attachments = self.template.make_schedule_template(
                MsgResource.UPDATE,
                {b_index: input_between}
            )
            self.slackbot.send_message(attachments=attachments)
        else:
            self.slackbot.send_message(text=MsgResource.ERROR)

    def delete(self, step=0, params=None):
        state = State()

        def step_0(params):
            self.slackbot.send_message(text=MsgResource.BETWEEN_DELETE_START)
            if self.read() == "success":
                state.flow_start("Between", "delete")

        def step_1(params):
            b_index = params
            self.data_handler.read_json_then_delete(
                self.fname, "between", b_index)

            state.flow_complete()
            self.slackbot.send_message(text=MsgResource.DELETE)

        locals()["step_" + str(step)](params)
