
from utils.data_handler import DataHandler

class State(object):

    def __init__(self):
        self.data_handler = DataHandler()
        self.fname = "state.json"
        self.current = self.data_handler.read_file(self.fname)

    def is_do_something(self):
        if self.current == {}:
            return False
        else:
            return True

    def start(self, class_name, func_name):
        doing = {"class": class_name, "def": func_name, "step": 1}
        self.data_handler.write_file(self.fname, doing)

    def next_step(self):
        step_num = self.current['step'] + 1
        self.current['step'] = step_num
        self.data_handler.write_file(self.fname, self.current)

    def complete(self):
        self.data_handler.write_file(self.fname, {})
