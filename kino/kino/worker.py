# -*- coding: utf-8 -*-

import json
import schedule
import threading

import functions
import nlp
import notifier
import slack
from slack import MsgResource
import utils

class Worker(object):

    def __init__(self, text):
        self.input = text
        self.slackbot = slack.SlackerAdapter()
        self.data_handler = utils.DataHandler()
        self.ner = nlp.NamedEntitiyRecognizer()

    def create(self):
        ner_time_of_day = self.ner.parse(self.ner.time_of_day, self.input)
        ner_time_unit = self.ner.parse(self.ner.time_unit, self.input, get_all=True)
        ner_period = self.ner.parse(self.ner.period, self.input)
        ner_functions = self.ner.parse(self.ner.functions, self.input)

        ner_dict = {
            "time_of_day": ner_time_of_day,
            "time_unit": ner_time_unit,
            "period": ner_period,
            "functions": ner_functions
        }
        notifier.Scheduler().create_with_ner(**ner_dict)

    def run(self):
        self.__set_schedules()
        schedule.run_continuously(interval=1)
        self.slackbot.send_message(text=MsgResource.WORKER_START)

    def __set_schedules(self):
        schedule_fname = "schedule.json"
        schedule_data = self.data_handler.read_file(schedule_fname)
        alarm_data = schedule_data.get('alarm', {})
        between_data = schedule_data.get('between', {})

        for k,v in alarm_data.items():
            if type(v) != type({}):
                continue

            if 'time' in v:
                time = v['time']
                # Do only once
                param = {
                    "repeat": False,
                    "func_name": v['f_name'],
                    "params": v.get('params', {})
                }

                try:
                    function = functions.FunctionManager().load_function
                    schedule.every().day.at(time).do(self.__run_threaded,
                                                            function, param)
                except Exception as e:
                    print("Error: " + e)

            if 'between_id' in v:
                between = between_data[v['between_id']]
                start_time, end_time = self.__time_interval2start_end(between['time_interval'])
                # Repeat
                period = v['period'].split(" ")
                number = int(period[0])
                datetime_unit = self.__replace_datetime_unit_ko2en(period[1])

                param = {
                    "start_time": start_time,
                    "end_time": end_time,
                    "repeat": True,
                    "func_name": v['f_name'],
                    "params": v.get('params', {})
                }

                try:
                    function = functions.FunctionManager().load_function
                    getattr(schedule.every(number), datetime_unit).do(self.__run_threaded,
                                                                    function, param)
                except Exception as e:
                    print("Error: " + e)


    def __replace_datetime_unit_ko2en(self, datetime_unit):
        ko2en_dict = {
            "초": "seconds",
            "분": "minutes",
            "시": "hours",
            "시간": "hours"
        }

        if datetime_unit in ko2en_dict:
            return ko2en_dict[datetime_unit]
        return datetime_unit

    def __time_interval2start_end(self, time_interval):
        if "~" in time_interval:
            time_interval = time_interval.split("~")
            start_time = time_interval[0].split(":")
            end_time = time_interval[1].split(":")

            start_time = tuple(map(lambda x: int(x), start_time))
            end_time = tuple(map(lambda x: int(x), end_time))
        else:
            start_time = time_interval
            end_time = None
        return start_time, end_time

    def __run_threaded(self, job_func, param):
        job_thread = threading.Thread(target=job_func, kwargs=param)
        job_thread.start()

    def stop(self):
        self.__set_schedules()
        schedule.clear()

        self.slackbot.send_message(text=MessageResource.WORKER_STOP)
