# -*- coding: utf-8 -*-

import json
import schedule
import threading

from functions.manager import FunctionManager
from notifier.between import Between
from slack.slackbot import SlackerAdapter
from kino.template import MsgTemplate
from utils.data_handler import DataHandler
from utils.resource import MessageResource
from utils.state import State

class Scheduler(object):

    def __init__(self):
        self.slackbot = SlackerAdapter()
        self.data_handler = DataHandler()
        self.fname = "scheduler.json"
        self.template = MsgTemplate()

    def create(self, step=0, params=None):

        state = State()

        def step_0(params):
            self.slackbot.send_message(text=MessageResource.SCHEDULER_CREATE_START)
            self.data_handler.read_json_then_add_data(self.fname, "alarm", {})
            state.start("Scheduler", "create")
            if Between().read() == "success":
                self.slackbot.send_message(text=MessageResource.SCHEDULER_CREATE_STEP1)
            else:
                self.slackbot.send_message(text=MessageResource.SCHEDULER_CREATE_STEP1_ONLY_TIME)

        def step_1(params):
            a_index, current_alarm_data = self.data_handler.get_current_data(self.fname, "alarm")

            if params.startswith("#"):
                current_alarm_data["between_id"] = params
                state.next_step()
                self.slackbot.send_message(text=MessageResource.SCHEDULER_CREATE_STEP2)
            else:
                current_alarm_data["time"] = params
                state.next_step(num=2)
                FunctionManager().read()
                self.slackbot.send_message(text=MessageResource.SCHEDULER_CREATE_STEP3)

            self.data_handler.read_json_then_edit_data(self.fname, "alarm", a_index, current_alarm_data)

        def step_2(params):
            a_index, current_alarm_data = self.data_handler.get_current_data(self.fname, "alarm")
            current_alarm_data["period"] = params
            self.data_handler.read_json_then_edit_data(self.fname, "alarm", a_index, current_alarm_data)

            state.next_step()
            FunctionManager().read()
            self.slackbot.send_message(text=MessageResource.SCHEDULER_CREATE_STEP3)

        def step_3(params):
            a_index, current_alarm_data = self.data_handler.get_current_data(self.fname, "alarm")

            if "," in params:
                f_name, f_params = params.split(",")
                current_alarm_data["f_name"] = f_name.strip()
                current_alarm_data["params"] = json.loads(f_params.strip().replace("”", "\"").replace("“", "\""))
            else:
                current_alarm_data["f_name"] = params.strip()
            self.data_handler.read_json_then_edit_data(self.fname, "alarm", a_index, current_alarm_data)

            state.complete()
            self.slackbot.send_message(text=MessageResource.CREATE)

        if state.is_do_something():
            current_step = state.current["step"]
            step_num = "step_" + str(current_step)
            locals()[step_num](params)
        else:
            step_0(params)

    def read(self):
        schedule_data = self.data_handler.read_file(self.fname)
        alarm_data = schedule_data.get('alarm', {})

        if alarm_data == {} or len(alarm_data) == 1:
            self.slackbot.send_message(text=MessageResource.EMPTY)
            return "empty"

        between_data = schedule_data.get('between', {})
        for k,v in alarm_data.items():
            if k == "index":
                continue

            if 'between_id' in v:
                between = between_data[v['between_id']]
                self.__alarm_in_between(between, k, v, repeat=True)
            elif 'time' in v:
                specific = between_data.get("#0", {})
                specific['description'] = "특정 시간 리스트."
                between_data["#0"] = self.__alarm_in_between(specific, k, v)

        attachments = self.template.make_schedule_template("", between_data)
        self.slackbot.send_message(text=MessageResource.READ, attachments=attachments)
        return "success"

    def __alarm_in_between(self, between, a_index, alarm_data, repeat=False):
        f_name = alarm_data['f_name']
        f_detail = FunctionManager().functions[f_name]

        if repeat:
            alarm_detail = "Alarm " + a_index + " (repeat: "+ alarm_data['period'] + ")\n"
        else:
            alarm_detail = "Alarm " + a_index + " (time: " + alarm_data['time'] + ")\n"

        alarm_detail += "            " + f_detail['icon'] + f_name + ", " + str(alarm_data.get('params', ''))
        registered_alarm = "등록된 알람 리스트."
        if registered_alarm in between:
            between[registered_alarm].append(alarm_detail)
        else:
            between[registered_alarm] = [alarm_detail]
        return between

    def update(self, step=0, params=None):
        a_index, input_text, input_period, input_between_id = params[0].split(" + ")
        input_alarm = {"text": input_text, "period": input_period, "between_id": input_between_id}

        result = self.data_handler.read_json_then_edit_data(self.fname, "alarm", a_index, input_alarm)

        if result == "sucess":
            attachments = self.template.make_schedule_template(
                MessageResource.UPDATE,
                {a_index:input_alarm}
            )

            self.slackbot.send_message(attachments=attachments)
        else:
            self.slackbot.send_message(text=MessageResource.ERROR)

    def delete(self, step=0, params=None):

        state = State()

        def step_0(params):
            self.slackbot.send_message(text=MessageResource.SCHEDULER_DELETE_START)
            if self.read() == "success":
                state.start("Scheduler", "delete")

        def step_1(params):
            a_index = params
            self.data_handler.read_json_then_delete(self.fname, "alarm", a_index)

            state.complete()
            self.slackbot.send_message(text=MessageResource.DELETE)

        if state.is_do_something():
            current_step = state.current["step"]
            step_num = "step_" + str(current_step)
            locals()[step_num](params)
        else:
            step_0(params)

