import re

import skills
import nlp
import kino
import notifier
import slack
from slack import MsgResource
import utils

class MsgRouter(object):

    def __init__(self):
        self.disintegrator = nlp.Disintegrator()
        self.state = nlp.State()
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

        # Check - help
        is_need_help = self.__help_call_bot(simple_text)
        if is_need_help:
            route_class = kino.Guide()
            behave = "help"
            self.logger.info("route to: " + route_class.__class__.__name__ + ", " + str(behave))
            getattr(route_class, behave)()
            return

        # Check - CRUD (Worker, Schedule, Between, FunctionManager)
        kino_keywords = {k: v['keyword'] for k,v in self.ner.kino.items()}
        classname = self.ner.parse(kino_keywords, simple_text)

        if classname is not None:
            class_dir, class_name = classname.split("/")
            route_class = getattr(globals()[class_dir], class_name)(text=text)
            behave_ner = self.ner.kino[classname]['behave']
            behave = self.ner.parse(behave_ner, simple_text)

            self.logger.info("route to: " + route_class.__class__.__name__ + ", " + str(behave))
            getattr(route_class, behave)()
            return

        # Check - skills
        skill_keywords = {k: v['keyword'] for k,v in self.ner.skills.items()}
        func_name = self.ner.parse(skill_keywords, text)
        if func_name is not None:
            func_param_list = self.ner.skills[func_name]['params']
            params = {k: self.ner.parse(v, text) for k,v in self.ner.params.items()}

            f_params = {}
            if params is not None:
                for k,v in params.items():
                    if k in func_param_list:
                        f_params[k] = v

            if func_name == "toggl_timer":
                f_params = {"description": text[text.index("toggl")+5:]}

            self.logger.info("From call skills - route to: " + func_name + ", " + str(f_params))
            getattr(skills.Functions(), func_name)(**f_params)
            return

        self.logger.info("not understanding")
        self.slackbot.send_message(text=MsgResource.NOT_UNDERSTANDING)
        return

    def __to_state_next_step(self, current_state):
        classname = current_state["class"]
        class_dir, class_name = classname.split("/")
        route_class = getattr(globals()[class_dir], class_name)()
        behave = current_state["def"]
        step_num = current_state["step"]
        return route_class, behave, step_num

    def __help_call_bot(self, text):
        if ("도움말" in text) or ("help" in text):
            return True
        return False
