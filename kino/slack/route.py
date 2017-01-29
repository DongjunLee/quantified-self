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
        self.slackbot = slack.SlackerAdapter()
        self.logger = utils.Logger().get_logger()

    def route(self, text=None, user=None):
        self.logger.info("raw input: " + text)

        # Preprocessing
        disintegrator = nlp.Disintegrator()
        simple_text = disintegrator.convert2simple(sentence=text)
        self.logger.info("clean input: " + simple_text)

        dialog_manager = nlp.DialogManager()

        # Check Dialog, Exercise
        if dialog_manager.is_call_write_diary(simple_text):
            skills.Summary().do_write_diary()
            self.slackbot.send_message(text=MsgResource.APPLAUD)
            return

        if dialog_manager.is_call_do_exercise(simple_text):
            skills.Summary().do_exercise()
            self.slackbot.send_message(text=MsgResource.APPLAUD)
            return

        # Check Flow
        if dialog_manager.is_on_flow():
            route_class, behave, step_num = dialog_manager.get_flow()
            self.logger.info("From Flow - route to: " + route_class.__class__.__name__ + ", " + str(behave))
            getattr(route_class, behave)(step=step_num, params=text)
            return

        # Check Memory
        if dialog_manager.is_on_memory() and dialog_manager.is_call_repeat_skill(text):
            route_class, func_name, params = dialog_manager.get_memory()
            self.logger.info("From Memory - route to: " + route_class.__class__.__name__ + ", " + str(func_name))
            f_params = dialog_manager.filter_f_params(text, func_name)
            if not f_params == {}:
                params = f_params
            getattr(route_class, func_name)(**params)
            return

        # Check - help
        if dialog_manager.is_call_help(simple_text):
            route_class = kino.Guide()
            behave = "help"
            self.logger.info("route to: " + route_class.__class__.__name__ + ", " + str(behave))
            getattr(route_class, behave)()
            return

        ner = nlp.NamedEntitiyRecognizer()

        # Check - CRUD (Worker, Schedule, Between, FunctionManager)
        kino_keywords = {k: v['keyword'] for k,v in ner.kino.items()}
        classname = ner.parse(kino_keywords, simple_text)

        if classname is not None:
            class_dir, class_name = classname.split("/")
            route_class = getattr(globals()[class_dir], class_name)(text=text)
            behave_ner = ner.kino[classname]['behave']
            behave = ner.parse(behave_ner, simple_text)

            self.logger.info("route to: " + route_class.__class__.__name__ + ", " + str(behave))
            getattr(route_class, behave)()
            return

        # Check - skills
        skill_keywords = {k: v['keyword'] for k,v in ner.skills.items()}
        func_name = ner.parse(skill_keywords, text)
        if func_name is not None:
            if dialog_manager.is_toggl_timer(func_name):
                f_params = {"description": text[text.index("toggl")+5:]}
            else:
                f_params = dialog_manager.filter_f_params(text, func_name)

            state = nlp.State()
            state.skill_memory(func_name, f_params)
            self.logger.info("From call skills - route to: " + func_name + ", " + str(f_params))
            getattr(skills.Functions(), func_name)(**f_params)
            return

        self.logger.info("not understanding")
        self.slackbot.send_message(text=MsgResource.NOT_UNDERSTANDING)
        return
