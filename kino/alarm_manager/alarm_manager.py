# -*- coding: utf-8 -*-

import datetime
import os
import random
import schedule
import threading
import time

from slacker import Slacker

from slack.template import MsgTemplate
from utils.data_handler import DataHandler

class AlarmManager(object):

    def __init__(self):
        SLACK_TOKEN = os.environ["STALKER_BOT_TOKEN"]
        self.slacker = Slacker(SLACK_TOKEN)
        self.data_handler = DataHandler()
        self.fname = "scheduler.json"
        self.template = MsgTemplate()

    def create(self, params):
        input_text, input_period, input_between_id = params[0].split(" + ")
        input_alarm = {"text": input_text, "period": input_period, "between_id": input_between_id}

        schedule_data, a_index = self.data_handler.read_json_then_add_data(self.fname, "alarm", input_alarm)

        attachments = self.template.make_schedule_template(
            "알람이 등록되었습니다.",
            {a_index:input_alarm}
        )

        self.slacker.chat.post_message(channel="#bot_test", text=None,
                                       attachments=attachments, as_user=True)

    def create_between(self, params):
        input_time_interval, input_description = params[0].split(" + ")
        input_between = {"time_interval": input_time_interval, "description": input_description, "color": self.__generate_color_code()}

        schedule_data, b_index = self.data_handler.read_json_then_add_data(self.fname, "between", input_between)

        attachments = self.template.make_schedule_template(
             "알람간격이 등록되었습니다.",
            {b_index:input_between}
        )

        self.slacker.chat.post_message(channel="#bot_test", text=None,
                                       attachments=attachments, as_user=True)

    def __generate_color_code(self):
        r = lambda: random.randint(0,255)
        color_code = '#%02X%02X%02X' % (r(),r(),r())
        return color_code

    def read(self, params):
        schedule_data = self.data_handler.read_file(self.fname)
        alarm_data = schedule_data.get('alarm', {})

        if alarm_data == {} or len(alarm_data) == 1:
            self.slacker.chat.post_message(channel="#bot_test",
                                           text="등록된 알람이 없습니다.",
                                           as_user=True)
            return ;n

        between_data = schedule_data.get('between', {})
        for k,v in alarm_data.items():
            if k == "index":
                continue
            between = between_data[v['between_id']]
            alarm_detail = "Alarm " + k + " => 텍스트: " + v['text'] + ", 주기: " + v['period']
            if 'alarm' in between:
                between['registerd_alarm'].append(alarm_detail)
            else:
                between['registerd_alarm'] = [alarm_detail]

        attachments = self.template.make_schedule_template("", between_data)
        self.slacker.chat.post_message(channel="#bot_test", text="알람 리스트.",
                                           attachments=attachments, as_user=True)

    def read_between(self, params):
        schedule_data = self.data_handler.read_file(self.fname)
        between_data = schedule_data.get('between', {})

        if between_data == {} or len(between_data) == 1:
            self.slacker.chat.post_message(channel="#bot_test",
                                           text="등록된 알람간격이 없습니다.",
                                           as_user=True)
        else:
            attachments = self.template.make_schedule_template("", between_data)
            self.slacker.chat.post_message(channel="#bot_test", text="알람간격 리스트.",
                                           attachments=attachments, as_user=True)

    def update(self, params):
        a_index, input_text, input_period, input_between_id = params[0].split(" + ")
        input_alarm = {"text": input_text, "period": input_period, "between_id": input_between_id}

        result = self.data_handler.read_json_then_edit_data(self.fname, "alarm", a_index, input_alarm)

        if result == "sucess":
            attachments = self.template.make_schedule_template(
                "알람이 변경되었습니다.",
                {a_index:input_alarm}
            )

            self.slacker.chat.post_message(channel="#bot_test", text=None,
                                           attachments=attachments, as_user=True)
        else:
            self.slacker.chat.post_message(channel="#bot_test", text="에러발생.", as_user=True)

    def update_between(self, params):
        b_index, input_time_interval, input_description = params[0].split(" + ")
        input_between = {"time_interval": input_time_interval, "description": input_description}

        result = self.data_handler.read_json_then_edit_data(self.fname, "between", b_index, input_between)

        if result == "sucess":
            attachments = self.template.make_schedule_template(
                "알람간격이 변경되었습니다.",
                {b_index:input_between}
            )

            self.slacker.chat.post_message(channel="#bot_test", text=None,
                                           attachments=attachments, as_user=True)
        else:
            self.slacker.chat.post_message(channel="#bot_test", text="에러발생.", as_user=True)

    def delete(self, params):
        a_index = params[0]

        self.data_handler.read_json_then_delete(self.fname, "alarm", a_index)
        self.slacker.chat.post_message(channel="#bot_test", text="알람이 삭제되었습니다.", as_user=True)

    def delete_between(self, params):
        b_index = params[0]

        self.data_handler.read_json_then_delete(self.fname, "between", b_index)
        self.slacker.chat.post_message(channel="#bot_test", text="알람간격이 삭제되었습니다.", as_user=True)

    def run_schedule(self, params):
        self.__set_schedules()
        schedule.run_continuously()

        self.slacker.chat.post_message(channel="#bot_test", text="알람기능을 시작합니다!",
                                       as_user=True)

    def __set_schedules(self):

        def send_message(text="input text", start_time=(7,0), end_time=(24,0)):
            now = datetime.datetime.now()
            now_6pm = now.replace(hour=start_time[0], minute=start_time[1], second=0, microsecond=0)
            now_11pm = now.replace(hour=end_time[0], minute=end_time[1], second=0, microsecond=0)
            if not(now_6pm < now < now_11pm):
                return
            else:
                self.slacker.chat.post_message(channel="#bot_test",
                                               text=text,
                                               as_user=True)

        schedule_data = self.data_handler.read_file(self.fname)
        alarm_data = schedule_data.get('alarm', {})
        between_data = schedule_data.get('between', {})

        for k,v in alarm_data.items():
            if type(v) == type({}):
                period = v['period'].split(" ")
                number = int(period[0])
                datetime_unit = self.__replace_datetime_unit_ko2en(period[1])
                between = between_data[v['between_id']]

                start_time, end_time = self.__time_interval2start_end(between['time_interval'])

                param = {
                    "text": v["text"],
                    "start_time": start_time,
                    "end_time": end_time
                }

                getattr(schedule.every(number), datetime_unit).do(self.__run_threaded,
                                                                  send_message, param)

    def __replace_datetime_unit_ko2en(self, datetime_unit):
        ko2en_dict = {
            "초": "seconds",
            "분": "minutes",
            "시간": "hours"
        }

        if datetime_unit in ko2en_dict:
            return ko2en_dict[datetime_unit]
        return datetime_unit

    def __time_interval2start_end(self, time_interval):
        time_interval = time_interval.split("~")
        start_time = time_interval[0].split(":")
        end_time = time_interval[1].split(":")

        start_time = tuple(map(lambda x: int(x), start_time))
        end_time = tuple(map(lambda x: int(x), end_time))

        return start_time, end_time

    def __run_threaded(self, job_func, param):
        job_thread = threading.Thread(target=job_func, kwargs=param)
        job_thread.start()

    def stop_schedule(self, params):
        self.__set_schedules()
        schedule.clear()

        self.slacker.chat.post_message(channel="#bot_test", text="알람기능을 중지합니다.",
                                       as_user=True)

