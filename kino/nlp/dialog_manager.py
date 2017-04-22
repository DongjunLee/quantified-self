
import arrow

import nlp
import skills
import slack
from slack import MsgResource
from utils import ArrowUtil, DataHandler


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

    def get_flow(self, is_raw=False):
        flow = self.current_state()[State.FLOW]
        if is_raw:
            return flow
        else:
            return self.__return_state(flow, State.FLOW)

    def is_on_memory(self):
        current_state = self.current_state()
        if "step" in current_state.get(State.MEMORY, {}):
            return True
        else:
            return False

    def get_memory(self, get_text=False):
        memory = self.current_state()[State.MEMORY]
        if get_text:
            return memory.get("text", None)
        else:
            return self.__return_state(memory, State.MEMORY)

    def get_action(self):
        return self.current_state().get(State.ACTION, None)

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
        params = {k: ner.parse(v, text) for k, v in ner.params.items()}

        f_params = {}
        if params is not None:
            for k, v in params.items():
                if k in func_param_list:
                    f_params[k] = v
        return f_params

    def is_toggl_timer(self, func_name):
        if func_name == "toggl_timer":
            return True
        else:
            return False

    def call_write_diary(self, text):
        if "일기" in text:
            skills.Summary().record_write_diary()
            self.slackbot.send_message(text=MsgResource.APPLAUD)

    def call_do_exercise(self, text):
        if "운동" in text:
            skills.Summary().record_exercise()
            self.slackbot.send_message(text=MsgResource.APPLAUD)

    def call_is_holiday(self, dnd):
        skills.Summary().record_holiday(dnd)
        if dnd:
            self.slackbot.send_message(text=MsgResource.HOLIDAY)
        else:
            self.slackbot.send_message(text=MsgResource.WEEKDAY)

    def check_wake_up(self, presence):
        record = self.data_handler.read_record()
        if 'wake_up' in record.get('activity', {}):
            return

        state = State()
        state.check()
        presence_log = state.current[state.SLEEP]
        if (ArrowUtil.is_between((6, 0), (11, 0)) and
                presence_log['presence'] == 'away' and presence == 'active'):
            self.slackbot.send_message(text=MsgResource.GOOD_MORNING)

            is_holiday = ArrowUtil.is_weekday() == False
            self.call_is_holiday(is_holiday)

            activity = record.get('activity', {})
            go_to_bed_time = arrow.get(activity.get('go_to_bed', None))

            wake_up_time = arrow.now()
            self.data_handler.edit_record_with_category(
                'activity', ('wake_up', str(wake_up_time)))

            sleep_time = (wake_up_time - go_to_bed_time).seconds / 60 / 60
            sleep_time = round(sleep_time * 100) / 100

            self.data_handler.edit_record(('Sleep', str(sleep_time)))

            self.slackbot.send_message(
                text=MsgResource.SLEEP_TIME(
                    go_to_bed_time.format("HH:mm"),
                    wake_up_time.format("HH:mm"),
                    str(sleep_time)))

            weather = skills.Weather()
            weather.forecast(timely="daily")
            weather.air_quality()

    def check_flow(self, presence):
        if presence == "active":
            flow = self.get_flow(is_raw=True)
            if flow.get('class', None) == "skills/Happy":
                self.slackbot.send_message(text=MsgResource.FLOW_HAPPY)

    def check_predictor(self, presence):
        flow = self.get_flow(is_raw=True)
        flow_class = flow.get('class', None)
        if presence == "active" and flow_class is None:
            functions = skills.Functions()
            functions.predict_skill()


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

    def memory_skill(self, text, func_name, params):
        data = {
            "text": text,
            "class": "skills/Functions",
            "def": func_name,
            "params": params
        }
        self.save(self.MEMORY, data)

    def do_action(self, event):
        time = ArrowUtil.get_action_time(event['time'])
        data = {
            "action": event['action'],
            "time": str(time)
        }
        self.save(self.ACTION, data)

    def presence_log(self, presence):
        data = {
            "presence": presence,
            "time": str(arrow.now())
        }
        self.save(self.SLEEP, data)
