# -*- coding: utf-8 -*-

import json
import schedule
import threading

import skills
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
        self.logger = utils.Logger().get_logger()
        self.ner = nlp.NamedEntitiyRecognizer()
        self.function = skills.FunctionManager().load_function

    def create(self):
        ner_dict = {k: self.ner.parse(v, self.input)
                    for k, v in self.ner.schedule.items()}
        time_unit = self.ner.parse(
            self.ner.schedule['time_unit'],
            self.input,
            get_all=True)
        ner_dict['time_unit'] = time_unit

        skill_keywords = {k: v['keyword'] for k, v in self.ner.skills.items()}
        func_name = self.ner.parse(skill_keywords, self.input)
        ner_dict['skills'] = func_name

        params = {k: self.ner.parse(v, self.input)
                  for k, v in self.ner.params.items()}
        ner_dict['params'] = params

        notifier.Scheduler().create_with_ner(**ner_dict)

    def run(self):
        self.set_schedules()
        schedule.run_continuously(interval=1)
        self.slackbot.send_message(text=MsgResource.WORKER_START)

    def set_schedules(self):
        self.__set_profile_schedule()
        self.__set_custom_schedule()

    def __set_profile_schedule(self):
        profile = utils.Profile()

        self.__excute_profile_schedule(
            profile.get_schedule('WAKE_UP'), False,
            'send_message', {"text": MsgResource.PROFILE_WAKE_UP}, True)

        self.__excute_profile_schedule(
            profile.get_schedule('WORK_START'), False,
            'send_message', {"text": MsgResource.PROFILE_WORK_START}, True)

        self.__excute_profile_schedule(
            profile.get_schedule('WORK_END'), False, 'send_message', {
                "text": MsgResource.PROFILE_WORK_END}, True)

        self.__excute_profile_schedule(
            profile.get_schedule('GO_TO_BED'), False,
            'send_message', {"text": MsgResource.PROFILE_GO_TO_BED}, False)

        self.__excute_profile_schedule(
            profile.get_schedule('CHECK_GO_TO_BED'), False,
            'check_go_to_bed', {}, False)

    def __excute_profile_schedule(
            self,
            time,
            repeat,
            func_name,
            params,
            not_holiday):
        schedule.every().day.at(time).do(
            self.__run_threaded, self.function, {
                "repeat": repeat,
                "func_name": func_name,
                "params": params,
                "not_holiday": not_holiday
            }
        )

    def __set_custom_schedule(self):
        schedule_fname = "schedule.json"
        schedule_data = self.data_handler.read_file(schedule_fname)
        alarm_data = schedule_data.get('alarm', {})
        between_data = schedule_data.get('between', {})

        for k, v in alarm_data.items():
            if not isinstance(v, type({})):
                continue

            if 'time' in v:
                time = v['time']
                param = {
                    # Do only once
                    "repeat": False,
                    "func_name": v['f_name'],
                    "params": v.get('f_params', {})
                }

                try:
                    function = skills.FunctionManager().load_function
                    schedule.every().day.at(time).do(self.__run_threaded,
                                                     function, param)
                except Exception as e:
                    print("Function Schedule Error: ", e)
                    self.slackbot.send_message(text=MsgResource.ERROR)

            if 'between_id' in v:
                between = between_data[v['between_id']]
                start_time, end_time = self.__time_interval2start_end(
                    between['time_interval'])
                # Repeat
                period = v['period'].split(" ")
                number = int(period[0])
                datetime_unit = self.__replace_datetime_unit_ko2en(period[1])

                param = {
                    "start_time": start_time,
                    "end_time": end_time,
                    "repeat": True,
                    "func_name": v['f_name'],
                    "params": v.get('f_params', {})
                }

                try:
                    function = skills.FunctionManager().load_function
                    getattr(
                        schedule.every(number),
                        datetime_unit).do(
                        self.__run_threaded,
                        function,
                        param)
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
        schedule.clear()

        self.slackbot.send_message(text=MsgResource.WORKER_STOP)
