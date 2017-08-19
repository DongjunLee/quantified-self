# -*- coding: utf-8 -*-

import json
import random

from .skill_list import SkillList

from .between import Between

from ..functions import RegisteredFuctions

from ..slack.resource import MsgResource
from ..slack.slackbot import SlackerAdapter
from ..slack.template import MsgTemplate

from ..utils.arrow import ArrowUtil
from ..utils.data_handler import DataHandler
from ..utils.state import State



class Scheduler(object):

    def __init__(self, text=None, slackbot=None):
        self.input = text
        self.data_handler = DataHandler()
        self.fname = "schedule.json"

        if slackbot is None:
            self.slackbot = SlackerAdapter()
        else:
            self.slackbot = slackbot

    def create(self, step=0, params=None):
        state = State()

        # 알람 생성 시작
        def step_0(params):
            self.slackbot.send_message(text=MsgResource.SCHEDULER_CREATE_START)
            self.data_handler.read_json_then_add_data(self.fname, "alarm", {})
            state.flow_start("Scheduler", "create")
            if Between().read() == "success":
                self.slackbot.send_message(
                    text=MsgResource.SCHEDULER_CREATE_STEP1)
            else:
                self.slackbot.send_message(
                    text=MsgResource.SCHEDULER_CREATE_STEP1_ONLY_TIME)

        # 시간대 지정
        def step_1(params):
            a_index, current_alarm_data = self.data_handler.get_current_data(
                self.fname, "alarm")

            if params.startswith("#"):
                current_alarm_data["between_id"] = params
                state.flow_next_step()
                self.slackbot.send_message(
                    text=MsgResource.SCHEDULER_CREATE_STEP2)
            else:
                current_alarm_data["time"] = params
                state.flow_next_step(num=2)
                SkillList().read()
                self.slackbot.send_message(
                    text=MsgResource.SCHEDULER_CREATE_STEP3)

            self.data_handler.read_json_then_edit_data(
                self.fname, "alarm", a_index, current_alarm_data)

        # 주기
        def step_2(params):
            a_index, current_alarm_data = self.data_handler.get_current_data(
                self.fname, "alarm")
            current_alarm_data["period"] = params
            self.data_handler.read_json_then_edit_data(
                self.fname, "alarm", a_index, current_alarm_data)

            state.flow_next_step()
            SkillList().read()
            self.slackbot.send_message(text=MsgResource.SCHEDULER_CREATE_STEP3)

        # 함수
        def step_3(params):
            a_index, current_alarm_data = self.data_handler.get_current_data(
                self.fname, "alarm")

            if "," in params:
                f_name, f_params = params.split(",")
                current_alarm_data["f_name"] = f_name.strip()
                current_alarm_data["params"] = json.loads(
                    f_params.strip().replace(
                        "”", "\"").replace(
                        "“", "\""))
            else:
                current_alarm_data["f_name"] = params.strip()
            self.data_handler.read_json_then_edit_data(
                self.fname, "alarm", a_index, current_alarm_data)

            state.flow_complete()
            self.slackbot.send_message(text=MsgResource.CREATE)

        locals()["step_" + str(step)](params)

    def create_with_ner(self, time_of_day=None, day_of_week=None, time_unit=None,
                        period=None, skills=None, params=None):

        if skills is None:
            self.slackbot.send_message(
                text=MsgResource.WORKER_FUNCTION_NOT_FOUND)
            return
        else:
            self.slackbot.send_message(text=MsgResource.WORKER_CREATE_START)

        if time_of_day is None:
            time_of_day = "all_day"
        if period == "real-time":
            period = "7 minutes"
        elif period == "interval":
            period = "interval"
        else:
            period = str(random.randint(25, 35)) + " minutes"

        if day_of_week is None:
            day_of_week = ['0']

        if time_unit is None:
            time = None
        elif len(time_unit) == 1 and period == "interval":
            period = time_unit[0]
            period = period.replace("분", " 분")
            period = period.replace("시", " 시")
            time = None
        else:
            time_of_day = None
            period = None

            time = ":"
            for t in time_unit:
                minute = 0
                if '시' in t:
                    hour = int(t[:t.index('시')])
                if '분' in t:
                    minute = int(t[:t.index('분')])
            time = '{0:02d}'.format(hour) + time + '{0:02d}'.format(minute)

        f_params = {}
        if params is not None:
            for k, v in params.items():
                if v is None:
                    continue
                f_params[k] = v

        alarm_data = {
            "between_id": time_of_day,
            "period": period,
            "time": time,
            "day_of_week": day_of_week,
            "f_name": skills,
            "f_params": f_params
        }

        alarm_data = dict((k, v) for k, v in alarm_data.items() if v)
        self.data_handler.read_json_then_add_data(
            self.fname, "alarm", alarm_data)
        self.slackbot.send_message(text=MsgResource.CREATE)

    def read(self):
        schedule_data = self.data_handler.read_file(self.fname)
        alarm_data = schedule_data.get('alarm', {})

        if alarm_data == {} or len(alarm_data) == 1:
            self.slackbot.send_message(text=MsgResource.EMPTY)
            return "empty"

        between_data = schedule_data.get('between', {})
        for k, v in alarm_data.items():
            if k == "index":
                continue

            if 'between_id' in v:
                between = between_data[v['between_id']]
                self.__alarm_in_between(between, k, v, repeat=True)
            elif 'time' in v:
                specific = between_data.get("specific time", {})
                specific['time_interval'] = ""
                specific['description'] = "특정 시간"
                between_data["specific time"] = self.__alarm_in_between(
                    specific, k, v)

        attachments = MsgTemplate.make_schedule_template("", between_data)
        self.slackbot.send_message(
            text=MsgResource.READ,
            attachments=attachments)
        return "success"

    def __alarm_in_between(self, between, a_index, alarm_data, repeat=False):
        f_name = alarm_data['f_name']
        f_detail = RegisteredFuctions().list[f_name]

        if repeat:
            key = "Alarm " + a_index + \
                " (repeat: " + alarm_data['period'] + ")"
        else:
            key = "Alarm " + a_index + " (time: " + alarm_data['time'] + ")"

        value = f_detail['icon'] + f_name + ", " + \
            str(alarm_data.get('f_params', '')) + " | " + ArrowUtil.format_day_of_week(alarm_data['day_of_week'])
        registered_alarm = "registered_alarm"
        if registered_alarm in between:
            between[registered_alarm][key] = value
        else:
            between[registered_alarm] = {key: value}
        return between

    def update(self, step=0, params=None):
        a_index, input_text, input_period, input_between_id = params[0].split(
            " + ")
        input_alarm = {
            "text": input_text,
            "period": input_period,
            "between_id": input_between_id}

        result = self.data_handler.read_json_then_edit_data(
            self.fname, "alarm", a_index, input_alarm)

        if result == "sucess":
            attachments = MsgTemplate.make_schedule_template(
                MsgResource.UPDATE,
                {a_index: input_alarm}
            )

            self.slackbot.send_message(attachments=attachments)
        else:
            self.slackbot.send_message(text=MsgResource.ERROR)

    def delete(self, step=0, params=None):
        state = State()

        def step_0(params):
            self.slackbot.send_message(text=MsgResource.SCHEDULER_DELETE_START)
            if self.read() == "success":
                state.flow_start("Scheduler", "delete")

        def step_1(params):
            a_index = params
            self.data_handler.read_json_then_delete(
                self.fname, "alarm", a_index)

            state.flow_complete()
            self.slackbot.send_message(text=MsgResource.DELETE)

        locals()["step_" + str(step)](params)
