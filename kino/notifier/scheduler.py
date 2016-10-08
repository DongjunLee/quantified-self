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

            Between().read()
            self.slackbot.send_message(text=MessageResource.SCHEDULER_CREATE_STEP1)

        def step_1(params):
            a_index, current_alarm_data = self.data_handler.get_current_data(self.fname, "alarm")
            current_alarm_data["between_id"] = params
            self.data_handler.read_json_then_edit_data(self.fname, "alarm", a_index, current_alarm_data)

            state.next_step()
            self.slackbot.send_message(text=MessageResource.SCHEDULER_CREATE_STEP2)

        def step_2(params):
            a_index, current_alarm_data = self.data_handler.get_current_data(self.fname, "alarm")
            current_alarm_data["period"] = params
            self.data_handler.read_json_then_edit_data(self.fname, "alarm", a_index, current_alarm_data)

            state.next_step()
            FunctionManager().read()
            self.slackbot.send_message(text=MessageResource.SCHEDULER_CREATE_STEP3)

        def step_3(params):
            a_index, current_alarm_data = self.data_handler.get_current_data(self.fname, "alarm")
            f_name, f_params = params.split(",")
            current_alarm_data["f_name"] = f_name.strip()
            current_alarm_data["params"] = json.loads(f_params.strip().replace("”", "\"").replace("“", "\""))
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
            return ;

        between_data = schedule_data.get('between', {})
        for k,v in alarm_data.items():
            if k == "index":
                continue
            between = between_data[v['between_id']]

            f_name = v['f_name']
            f_detail = FunctionManager().functions[f_name]

            alarm_detail = "Alarm " + k + " (repeat: "+ v['period'] +")" + "\n"
            alarm_detail += "            " + f_detail['icon'] + f_name + ", " + str(v['params'])
            if 'alarm' in between:
                between['registerd_alarm'].append(alarm_detail)
            else:
                between['registerd_alarm'] = [alarm_detail]

        attachments = self.template.make_schedule_template("", between_data)
        self.slackbot.send_message(text=MessageResource.READ, attachments=attachments)

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
        a_index = params[0]
        self.data_handler.read_json_then_delete(self.fname, "alarm", a_index)
        self.slackbot.send_message(text=MessageResource.DELETE)

    def run(self):
        self.__set_schedules()
        schedule.run_continuously(interval=1)
        self.slackbot.send_message(text=MessageResource.NOTIFIER_START)

    def __set_schedules(self):

#        def send_message(text="input text", start_time=(7,0), end_time=(24,0)):
#            now = datetime.datetime.now()
#            now_6pm = now.replace(hour=start_time[0], minute=start_time[1], second=0, microsecond=0)
#            now_11pm = now.replace(hour=end_time[0], minute=end_time[1], second=0, microsecond=0)
#            if not(now_6pm < now < now_11pm):
#                return
#            else:
#                self.slacker.chat.post_message(channel="#bot_test",
#                                               text=text,
#                                               as_user=True)

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
                    "start_time": start_time,
                    "end_time": end_time,
                    "func_name": v['f_name'],
                    "params": v['params']
                }

                function = FunctionManager().load_function
                getattr(schedule.every(number), datetime_unit).do(self.__run_threaded,
                                                                  function, param)

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

    def stop(self):
        self.__set_schedules()
        schedule.clear()

        self.slackbot.send_message(text=MessageResource.NOTIFIER_STOP)
