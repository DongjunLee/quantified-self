
import nlp
import notifier
import skills
from utils.data_handler import DataHandler

class DialogManager(object):

    def __init__(self):
        self.state = State()

    def current_state(self):
        self.state.check()
        return self.state.current

    def is_on_flow(self):
        self.state.check()
        if ("kind" in self.state.current) and self.state.current["kind"] == State.FLOW:
            return True
        else:
            return False

    def get_flow(self):
        current_state = self.current_state()
        classname = current_state["class"]
        class_dir, class_name = classname.split("/")
        route_class = getattr(globals()[class_dir], class_name)()
        behave = current_state["def"]
        step_num = current_state["step"]
        return route_class, behave, step_num

    def is_on_memory(self):
        self.state.check()
        if ("kind" in self.state.current) and self.state.current["kind"] == State.MEMORY:
            return True
        else:
            return False

    def get_memory(self):
        current_state = self.current_state()
        classname = current_state["class"]
        class_dir, class_name = classname.split("/")
        route_class = getattr(globals()[class_dir], class_name)()
        behave = current_state["def"]
        params = current_state["params"]
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

    def is_call_write_diary(self, text):
        if "일기 쓰다" in text:
            return True
        else:
            return False

    def is_call_do_exercise(self, text):
        if "운동 하다" in text:
            return True
        else:
            return False

class State(object):

    FLOW = "flow"
    MEMORY = "memory"

    def __init__(self):
        self.data_handler = DataHandler()
        self.fname = "state.json"
        self.current = None

    def check(self):
        self.current = self.data_handler.read_file(self.fname)

    def start(self, class_name, func_name):
        doing = {
            "class": class_name,
            "def": func_name,
            "step": 1,
            "kind": self.FLOW
        }
        self.data_handler.write_file(self.fname, doing)

    def next_step(self, num=1):
        step_num = self.current['step'] + num
        self.current['step'] = step_num
        self.data_handler.write_file(self.fname, self.current)

    def complete(self):
        self.data_handler.write_file(self.fname, {})

    def skill_memory(self, func_name, params):
        memory = {
            "class": "skills/Functions",
            "def": func_name,
            "params": params,
            "kind": self.MEMORY
        }
        self.data_handler.write_file(self.fname, memory)
