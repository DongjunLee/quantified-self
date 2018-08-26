# -*- coding: utf-8 -*-

import arrow

from .arrow import ArrowUtil
from .data_handler import DataHandler


class State(object):

    FLOW = "flow"
    MEMORY = "memory"
    ACTION = "action"
    SLEEP = "sleep"
    REST = "rest"

    def __init__(self):
        self.data_handler = DataHandler()
        self.fname = "state.json"
        self.current = None

    def check(self):
        self.current = self.data_handler.read_file(self.fname)

    def save(self, key, value):
        self.check()
        self.current[key] = value
        self.data_handler.write_file(self.fname, self.current)

    def flow_start(self, class_name, func_name):
        data = {"class": class_name, "def": func_name, "step": 1}
        self.save(self.FLOW, data)

    def flow_next_step(self, num=1):
        self.check()
        current_flow = self.current[self.FLOW]
        step_num = current_flow["step"] + num
        current_flow["step"] = step_num
        self.data_handler.write_file(self.fname, self.current)

    def flow_complete(self):
        self.save(self.FLOW, {})

    def memory_skill(self, text, func_name, params):
        data = {"text": text, "class": "Functions", "def": func_name, "params": params}
        self.save(self.MEMORY, data)

    def do_action(self, event):
        time = ArrowUtil.get_action_time(event["time"])
        data = {"action": event["action"], "time": str(time)}
        self.save(self.ACTION, data)

    def presence_log(self, user, presence):
        data = {"user": user, "presence": presence, "time": str(arrow.now())}
        self.save(self.SLEEP, data)

    def advice_rest(self, diff_min):
        rest_mins = 0
        if diff_min > 100:
            rest_mins = 20
        elif diff_min > 60:
            rest_mins = 6 + diff_min // 10

        now = arrow.now()
        advice = now.replace(minutes=rest_mins)

        data = {"time": str(advice), "try": False}
        self.save(self.REST, data)

    def advice_check(self):
        self.check()
        rest_state = self.current.get(self.REST)

        rest_state["try"] = True
        self.save(self.REST, rest_state)

