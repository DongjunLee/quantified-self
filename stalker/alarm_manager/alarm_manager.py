# -*- coding: utf-8 -*-

import os
import schedule
import threading
import time

from slacker import Slacker
from utils.data_handler import DataHandler

class AlarmManager(object):

    def __init__(self):
        SLACK_TOKEN = os.environ["STALKER_BOT_TOKEN"]
        self.slacker = Slacker(SLACK_TOKEN)
        self.data_handler = DataHandler()
        self.fname = "scheduler.json"

    def create(self, params):
        print("alarm create!!")
        params = params[0].split(" + ")
        input_text = params[0]
        input_period = params[1]

        schedule_data = self.data_handler.read_file(self.fname)

        if schedule_data == {}:
            s_index = 1
        else:
            s_index = schedule_data['count'] + 1

        input_schedule = { "text": input_text, "period": input_period}
        schedule_data[s_index] = input_schedule
        schedule_data["count"] = s_index

        self.data_handler.write_file(self.fname, schedule_data)
        self.slacker.chat.post_message(channel="#bot_test",
                                       text="알람이 등록되었습니다.",
                                       as_user=True)


    def read(self, params):
        print("alarm read!!")
        print(params)

    def update(self, params):
        print("alarm update!!")
        print(params)

    def delete(self, params):
        print("alarm delete!!")
        print(params)

    def run_schedule(self):
        self.__set_schedules()
        schedule.run_continuously()

    def __set_schedules(self):

        def send_message(text="input text"):
            self.slacker.chat.post_message(channel="#bot_test",
                                           text=text,
                                           as_user=True)

        schedule_data = self.data_handler.read_file(self.fname)
        for k,v in schedule_data.items():
            if type(v) == type({}):
                period = v["period"].split(" ")
                number = int(period[0])
                datetime_unit = period[1]
                param = {"text": v["text"]}

                getattr(schedule.every(number), datetime_unit).do(self.__run_threaded,
                                                                  send_message, param)

    def __run_threaded(self, job_func, param):
        job_thread = threading.Thread(target=job_func, kwargs=param)
        job_thread.start()

