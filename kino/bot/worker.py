# -*- coding: utf-8 -*-

import threading

from hbconfig import Config

from ..background import schedule

from ..functions import FunctionRunner

from ..nlp.ner import NamedEntitiyRecognizer

from ..notifier.scheduler import Scheduler

from ..slack.resource import MsgResource
from ..slack.slackbot import SlackerAdapter

from ..utils.data_handler import DataHandler
from ..utils.logger import Logger


class Worker(object):
    def __init__(self, text=None, slackbot=None):
        self.input = text
        self.data_handler = DataHandler()
        self.logger = Logger().get_logger()
        self.ner = NamedEntitiyRecognizer()
        self.function_runner = FunctionRunner().load_function

        if slackbot is None:
            self.slackbot = SlackerAdapter()
        else:
            self.slackbot = slackbot

        if Config.profile.personal:
            from ..utils.profile import Profile

            self.profile = Profile()
        else:
            self.profile = None

    def create(self):
        ner_dict = {
            k: self.ner.parse(v, self.input) for k, v in self.ner.schedule.items()
        }

        day_of_week = self.ner.parse(
            self.ner.schedule["day_of_week"], self.input, get_all=True
        )
        ner_dict["day_of_week"] = day_of_week

        time_unit = self.ner.parse(
            self.ner.schedule["time_unit"], self.input, get_all=True
        )
        ner_dict["time_unit"] = time_unit

        skill_keywords = {k: v["keyword"] for k, v in self.ner.skills.items()}
        func_name = self.ner.parse(skill_keywords, self.input)
        ner_dict["skills"] = func_name

        params = {k: self.ner.parse(v, self.input) for k, v in self.ner.params.items()}
        ner_dict["params"] = params

        Scheduler().create_with_ner(**ner_dict)

    def run(self, init=False):
        if self.is_running():
            return

        self.set_schedules()
        schedule.run_continuously(interval=1)

        if not init:
            self.slackbot.send_message(text=MsgResource.WORKER_START)

    def is_running(self):
        if len(schedule.jobs) > 0:
            return True
        else:
            return False

    def set_schedules(self):
        if self.profile:
            self.__set_profile_schedule()
        self.__set_custom_schedule()

    def __set_profile_schedule(self):

        self.__excute_profile_schedule(
            self.profile.get_schedule("WAKE_UP"),
            False,
            "good_morning",
            {},
            True,
        )

        self.__excute_profile_schedule(
            self.profile.get_schedule("WORK_START"),
            False,
            "send_message",
            {"text": MsgResource.PROFILE_WORK_START},
            True,
        )

        self.__excute_profile_schedule(
            self.profile.get_schedule("WORK_END"),
            False,
            "send_message",
            {"text": MsgResource.PROFILE_WORK_END},
            True,
        )

        self.__excute_profile_schedule(
            self.profile.get_schedule("GO_TO_BED"),
            False,
            "good_night",
            {},
            False,
        )

        # Toggl Tasks <-> Activity Tasks Sync
        self.__excute_profile_schedule(
            "23:55",
            False,
            "activity_task_sync",
            {},
            False,
        )

        # slack presence issue
        # self.__excute_profile_schedule(
        # self.profile.get_schedule('CHECK_GO_TO_BED'), False,
        # 'check_go_to_bed', {}, False)

        interval = Config.profile.feed.INTERVAL
        self.__excute_feed_schedule(interval)
        self.__excute_health_check()

    def __excute_profile_schedule(self, time, repeat, func_name, params, not_holiday):
        schedule.every().day.at(time).do(
            self.__run_threaded,
            self.function_runner,
            {
                "repeat": repeat,
                "func_name": func_name,
                "params": params,
                "day_of_week": [0],
                "not_holiday": not_holiday,
            },
        )

    def __excute_feed_schedule(self, interval):
        schedule.every(interval).minutes.do(
            self.__run_threaded,
            self.function_runner,
            {
                "repeat": True,
                "func_name": "feed_notify",
                "params": {},
                "day_of_week": [0],
                "not_holiday": False,
            },
        )

    def __excute_health_check(self):
        schedule.every(30).minutes.do(
            self.__run_threaded,
            self.function_runner,
            {
                "repeat": True,
                "func_name": "health_check",
                "params": {},
                "day_of_week": [0],
                "not_holiday": False,
            },
        )

    def __set_custom_schedule(self):
        schedule_fname = "schedule.json"
        schedule_data = self.data_handler.read_file(schedule_fname)
        alarm_data = schedule_data.get("alarm", {})
        between_data = schedule_data.get("between", {})

        for _, v in alarm_data.items():
            if not isinstance(v, type({})):
                continue

            day_of_week = v.get("day_of_week", [0])

            if "time" in v:
                time = v["time"]
                param = {
                    # Do only once
                    "repeat": False,
                    "func_name": v["f_name"],
                    "day_of_week": day_of_week,
                    "params": v.get("f_params", {}),
                }

                try:
                    schedule.every().day.at(time).do(
                        self.__run_threaded, self.function_runner, param
                    )
                except Exception as e:
                    print("Function Schedule Error: ", e)
                    self.slackbot.send_message(text=MsgResource.ERROR)

            if "between_id" in v:
                between = between_data[v["between_id"]]
                start_time, end_time = self.__time_interval2start_end(
                    between["time_interval"]
                )
                # Repeat
                period = v["period"].split(" ")
                number = int(period[0])
                datetime_unit = self.__replace_datetime_unit_ko2en(period[1])

                param = {
                    "start_time": start_time,
                    "end_time": end_time,
                    "repeat": True,
                    "day_of_week": day_of_week,
                    "func_name": v["f_name"],
                    "params": v.get("f_params", {}),
                }

                try:
                    getattr(schedule.every(number), datetime_unit).do(
                        self.__run_threaded, self.function_runner, param
                    )
                except Exception as e:
                    print("Error: " + e)

    def __replace_datetime_unit_ko2en(self, datetime_unit):
        ko2en_dict = {"초": "seconds", "분": "minutes", "시": "hours", "시간": "hours"}

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

    def stop(self, init=False):
        schedule.clear()

        if not init:
            self.slackbot.send_message(text=MsgResource.WORKER_STOP)
