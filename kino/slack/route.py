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

        if self.state.is_do_something():
            current_state = self.state.current
            route_class, behave, step_num = self.__to_state_next_step(current_state)
            getattr(route_class, behave)(step=step_num, params=text)
            return

        simple_text = self.disintegrator.convert2simple(sentence=text)
        self.logger.info("clean input: " + simple_text)

        is_greeting = self.__greeting_call_bot(simple_text)
        is_call_worker = self.__worker_call_bot(simple_text)

        if is_call_worker:
            route_class = kino.Worker(text=text)
            behave = self.ner.parse(self.ner.kino['behave'], simple_text)
        else:
            classname = self.ner.parse(self.ner.classname, simple_text)

            if classname == "not exist":
                route_class = None
                behave = "not exist"
            else:
                class_dir, class_name = classname.split("/")
                route_class = getattr(globals()[class_dir], class_name)(text=text)
                behave_ner = self.ner.behave[classname]
                behave = self.ner.parse(behave_ner, simple_text)
                params = self.ner.parse(self.ner.params, simple_text)

        self.logger.info("route to: " + route_class.__class__.__name__ + ", " + behave)
        if behave == "help":
            route_class = Guide()
            getattr(route_class, behave)()
        elif route_class == functions.YoutubeDownloader(text):
            getattr(route_class, "make_link")()
        elif (route_class == None or behave == "not exist") and is_greeting:
            pass
        elif route_class == None or behave == "not exist":
            self.slackbot.send_message(text=MsgResource.NOT_UNDERSTANDING)
        else:
            getattr(route_class, behave)()

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

    def __worker_call_bot(self, text):
        if any([p for p in self.ner.kino['Worker'] if p in text]):
            return True
        return False
