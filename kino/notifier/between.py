# -*- coding: utf-8 -*-

import random

from kino.template import MsgTemplate
from slack.slackbot import SlackerAdapter
from utils.data_handler import DataHandler
from utils.resource import MessageResource
from utils.state import State

class Between(object):

    def __init__(self):
        self.slackbot = SlackerAdapter()
        self.data_handler = DataHandler()
        self.fname = "scheduler.json"
        self.template = MsgTemplate()

    def create(self, step=0, params=None):

        state = State()

        def step_0(params):
            self.slackbot.send_message(text=MessageResource.BETWEEN_CREATE_START)
            self.data_handler.read_json_then_add_data(self.fname, "between", {})
            state.start("Between", "create")

            self.slackbot.send_message(text=MessageResource.BETWEEN_CREATE_STEP1)

        def step_1(params):
            b_index, current_between_data = self.data_handler.get_current_data(self.fname, "between")
            current_between_data['time_interval'] = params
            self.data_handler.read_json_then_edit_data(self.fname, "between", b_index, current_between_data)

            state.next_step()
            self.slackbot.send_message(text=MessageResource.BETWEEN_CREATE_STEP2)

        def step_2(params):
            b_index, current_between_data = self.data_handler.get_current_data(self.fname, "between")
            current_between_data['color'] = self.__generate_color_code()
            current_between_data['description'] = params
            self.data_handler.read_json_then_edit_data(self.fname, "between", b_index, current_between_data)

            state.complete()
            self.slackbot.send_message(text=MessageResource.CREATE)

        if state.is_do_something():
            current_step = state.current["step"]
            step_num = "step_" + str(current_step)
            locals()[step_num](params)
        else:
            step_0(params)

    def __generate_color_code(self):
        r = lambda: random.randint(0,255)
        color_code = '#%02X%02X%02X' % (r(),r(),r())
        return color_code

    def read(self):
        attachments = self.__make_between_list()
        if attachments == None:
            self.slackbot.send_message(text=MessageResource.EMPTY)
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
        b_index, input_time_interval, input_description = params[0].split(" + ")
        input_between = {"time_interval": input_time_interval, "description": input_description}

        result = self.data_handler.read_json_then_edit_data(self.fname, "between", b_index, input_between)

        if result == "sucess":
            attachments = self.template.make_schedule_template(
                MessageResource.UPDATE,
                {b_index:input_between}
            )
            self.slackbot.send_message(attachments=attachments)
        else:
            self.slackbot.send_message(text=MessageResource.ERROR)

    def delete(self, step=0, params=None):

        state = State()

        def step_0(params):
            self.slackbot.send_message(text=MessageResource.BETWEEN_DELETE_START)
            if self.read() == "success":
                state.start("Between", "delete")

        def step_1(params):
            b_index = params
            self.data_handler.read_json_then_delete(self.fname, "between", b_index)

            state.complete()
            self.slackbot.send_message(text=MessageResource.DELETE)

        if state.is_do_something():
            current_step = state.current["step"]
            step_num = "step_" + str(current_step)
            locals()[step_num](params)
        else:
            step_0(params)


