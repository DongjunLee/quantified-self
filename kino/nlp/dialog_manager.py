
import arrow

import nlp
import notifier
import skills
import slack
from slack import MsgResource
from utils.data_handler import DataHandler

class DialogManager(object):

    def __init__(self):
        self.state = State()
        self.slackbot = slack.SlackerAdapter()
        self.data_handler = DataHandler()

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

    def call_good_morning(self, text):
        if "굿모닝" in text:
            self.slackbot.send_message(text=MsgResource.GOOD_MORNING)

            skills.Summary().record_good_morning()
            record = self.data_handler.read_record()

            good_morning = arrow.get(record['GoodMorning'])
            good_night = arrow.get(record['GoodNight'])

            sleep_time = (good_morning - good_night).seconds / 60 / 60
            sleep_time = round(sleep_time*100)/100

            self.slackbot.send_message(text=MsgResource.SLEEP_TIME(
                good_night.format("HH:mm"), good_morning.format("HH:mm"), str(sleep_time)
            ))
            return True
        else:
            return False

    def call_good_night(self, text):
        if "굿나잇" in text:
            skills.Summary().record_good_night()
            self.slackbot.send_message(text=MsgResource.GOOD_NIGHT)
            return True
        else:
            return False

class State(object):

    FLOW = "flow"
    MEMORY = "memory"
    ACTION = "action"

    def __init__(self):
        self.data_handler = DataHandler()
        self.fname = "state.json"
        self.current = None

    def check(self):
        self.current = self.data_handler.read_file(self.fname)

    def flow_start(self, class_name, func_name):
        doing = {
            "class": class_name,
            "def": func_name,
            "step": 1
        }
        self.check()
        self.current[self.FLOW] = doing
        self.data_handler.write_file(self.fname, self.current)

    def flow_next_step(self, num=1):
        self.check()
        current_flow = self.current[self.FLOW]
        step_num = current_flow['step'] + num
        current_flow['step'] = step_num
        self.data_handler.write_file(self.fname, self.current)

    def flow_complete(self):
        self.check()
        self.current[self.FLOW] = {}
        self.data_handler.write_file(self.fname, self.current)

    def memory_skill(self, func_name, params):
        memory = {
            "class": "skills/Functions",
            "def": func_name,
            "params": params
        }
        self.check()
        self.current[self.MEMORY] = memory
        self.data_handler.write_file(self.fname, self.current)

    def do_action(self, action, time):
        time = arrow.get(time)
        do = {
            "action": action,
            "time": str(time)
        }
        self.check()
        self.current[self.ACTION] = do
        self.data_handler.write_file(self.fname, self.current)
