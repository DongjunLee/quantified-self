import re

import functions
import nlp
import kino
import notifier
import slack
from slack import MsgResource
import utils

class MsgRouter(object):

    def __init__(self):
        self.disintegrator = nlp.Disintegrator()
        self.state = utils.State()
        self.slackbot = slack.SlackerAdapter()
        self.logger = utils.Logger().get_logger()
        self.ner = nlp.NamedEntitiyRecognizer()

    def route(self, text=None, user=None):
        self.logger.info("raw input: " + text)

        # Check State
        if self.state.is_do_something():
            current_state = self.state.current
            route_class, behave, step_num = self.__to_state_next_step(current_state)
            self.logger.info("From State - route to: " + route_class.__class__.__name__ + ", " + str(behave))
            getattr(route_class, behave)(step=step_num, params=text)
            return

        # Preprocessing
        simple_text = self.disintegrator.convert2simple(sentence=text)
        self.logger.info("clean input: " + simple_text)

        # Check - greeting, help, and call worker
        is_greeting = self.__greeting_call_bot(simple_text)
        is_need_help = self.__help_call_bot(simple_text)
        if is_need_help:
            route_class = kino.Guide()
            behave = "help"
            self.logger.info("route to: " + route_class.__class__.__name__ + ", " + str(behave))
            getattr(route_class, behave)()
            return

        is_call_worker = self.__worker_call_bot(simple_text)
        if is_call_worker:
            route_class = kino.Worker(text=text)
            behave = self.ner.parse(self.ner.kino['behave'], simple_text)
            self.logger.info("From call worder - route to: " + route_class.__class__.__name__ + ", " + str(behave))
            getattr(route_class, behave)()
            return

        # Check - Functions
        func_name = self.ner.parse(self.ner.functions, text)
        if func_name is not None:
            params = self.ner.parse(self.ner.params[func_name], text)

            f_params = {}
            if params is not None:
                for p in params:
                    key, value = p
                    f_params[key] = value


            if func_name == "toggl_timer":
                f_params = {"description": text[text.index("toggl")+5:]}

            self.logger.info("From call functions - route to: " + func_name + ", " + str(f_params))
            getattr(functions.Functions(), func_name)(**f_params)
            return

        # Check - CRUD (Schedule, Between, FunctionManager)
        classname = self.ner.parse(self.ner.classname, simple_text)

        if classname is None:
            self.slackbot.send_message(text=MsgResource.NOT_UNDERSTANDING)
            return

        class_dir, class_name = classname.split("/")
        route_class = getattr(globals()[class_dir], class_name)(text=text)
        behave_ner = self.ner.behave[classname]
        behave = self.ner.parse(behave_ner, simple_text)
        params = self.ner.parse(self.ner.params, simple_text)

        if route_class == functions.YoutubeDownloader(text):
            self.logger.info("route to: " + route_class.__class__.__name__ + ", " + str(behave))
            getattr(route_class, "make_link")()
            return

        if (route_class == None or behave == "not exist") and not is_greeting:
            self.slackbot.send_message(text=MsgResource.NOT_UNDERSTANDING)

        self.logger.info("route to: " + route_class.__class__.__name__ + ", " + str(behave))
        getattr(route_class, behave)()
        return

    def __to_state_next_step(self, current_state):
        classname = current_state["class"]
        class_dir, class_name = classname.split("/")
        route_class = getattr(globals()[class_dir], class_name)()
        behave = current_state["def"]
        step_num = current_state["step"]
        return route_class, behave, step_num

    def __greeting_call_bot(self, text):
        if any([p for p in self.ner.kino['name'] if p in text]):
            self.slackbot.send_message(text=MsgResource.GREETING)
            return True
        return False

    def __help_call_bot(self, text):
        if ("도움말" in text) or ("help" in text):
            return True
        return False

    def __worker_call_bot(self, text):
        for k in self.ner.kino['Worker']:
            for t in text.split(" "):
                if k == t:
                    return True
        return False
