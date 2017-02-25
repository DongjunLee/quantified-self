
import arrow
from dateutil import tz

import nlp
import notifier
import skills
import slack
from slack import MsgResource
import utils
from utils.data_handler import DataHandler

class DialogManager(object):

    def __init__(self):
        self.state = State()
        self.slackbot = slack.SlackerAdapter()
        self.data_handler = DataHandler()
        self.arrow_util = utils.ArrowUtil()

    def current_state(self):
        self.state.check()
        return self.state.current

    def is_on_flow(self):
        current_state = self.current_state()
        if "step" in current_state.get(State.FLOW, {}):
            return True
        else:
            return False

    def get_flow(self):
        flow = self.current_state()[State.FLOW]
        return self.__return_state(flow, State.FLOW)

    def is_on_memory(self):
        current_state = self.current_state()
        if "step" in current_state.get(State.MEMORY, {}):
            return True
        else:
            return False

    def get_memory(self):
        memory = self.current_state()[State.MEMORY]
        return self.__return_state(memory, State.MEMORY)

    def get_action(self):
        return self.current_state()[State.ACTION]

    def __return_state(self, state, kind):
        classname = state["class"]
        class_dir, class_name = classname.split("/")
        route_class = getattr(globals()[class_dir], class_name)()
        behave = state["def"]
        if kind == State.FLOW:
            params = state["step"]
        elif kind == State.MEMORY:
            params = state["params"]
        return route_class, behave, params

    def is_call_repeat_skill(self, text):
        if "다시" in text:
            return True
        else:
            False

    def is_call_help(self, text):
        if ("도움말" in text) or ("help" in text):
            return True
        else:
            return False

    def filter_f_params(self, text, func_name):
        ner = nlp.NamedEntitiyRecognizer()

        func_param_list = ner.skills[func_name]['params']
        params = {k: ner.parse(v, text) for k,v in ner.params.items()}

        f_params = {}
        if params is not None:
            for k,v in params.items():
                if k in func_param_list:
                    f_params[k] = v
        return f_params

    def is_toggl_timer(self, func_name):
        if func_name == "toggl_timer":
            return True
        else:
            return False

    def call_write_diary(self, text):
        if "일기 쓰다" in text:
            skills.Summary().record_write_diary()
            self.slackbot.send_message(text=MsgResource.APPLAUD)
            return True
        else:
            return False

    def call_do_exercise(self, text):
        if "운동 하다" in text:
            skills.Summary().record_exercise()
            self.slackbot.send_message(text=MsgResource.APPLAUD)
            return True
        else:
            return False

    def check_wake_up(self, text):
        record = self.data_handler.read_record()
        if 'wake_up' in record.get('activity', {}):
            return

        state = State()
        state.check()
        presence_log = state.current[state.SLEEP]
        if self.arrow_util.is_between((6,0), (11,0)) and presence_log['presence'] == 'away':
            self.slackbot.send_message(text=MsgResource.GOOD_MORNING)

            go_to_bed_time = arrow.get(presence_log['time'])
            wake_up_time = arrow.now()

            self.data_handler.edit_record_with_category('activity', ('go_to_bed', str(go_to_bed_time)))
            self.data_handler.edit_record_with_category('activity', ('wake_up', str(wake_up_time)))

            sleep_time = (wake_up_time - go_to_bed_time).seconds / 60 / 60
            sleep_time = round(sleep_time*100)/100

            self.data_handler.edit_record('Sleep', str(sleep_time))

            self.slackbot.send_message(text=MsgResource.SLEEP_TIME(
                good_night.format("HH:mm"), good_morning.format("HH:mm"), str(sleep_time)
            ))

class State(object):

    FLOW = "flow"
    MEMORY = "memory"
    ACTION = "action"
    SLEEP = "sleep"

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
        data = {
            "class": class_name,
            "def": func_name,
            "step": 1
        }
        self.save(self.FLOW, data)

    def flow_next_step(self, num=1):
        self.check()
        current_flow = self.current[self.FLOW]
        step_num = current_flow['step'] + num
        current_flow['step'] = step_num
        self.data_handler.write_file(self.fname, self.current)

    def flow_complete(self):
        self.save(self.FLOW, {})

    def memory_skill(self, func_name, params):
        data = {
            "class": "skills/Functions",
            "def": func_name,
            "params": params
        }
        self.save(self.MEMORY, data)

    def do_action(self, event):
        time = self.arrow_util.get_action_time(event['time'])
        data = {
            "action": event['action'],
            "time": str(time)
        }
        self.save(self.ACTION, data)

    def presence_log(self, log):
        data = {
            "presence": log['presence'],
            "time": str(arrow.now())
        }
        self.save(self.SLEEP, data)
