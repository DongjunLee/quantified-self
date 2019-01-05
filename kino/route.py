
import json
import random

from hbconfig import Config

from .functions import Functions
from .functions import FunctionRunner
from .webhook import Webhook

from .dialog.dialog_manager import DialogManager
from .dialog.dnd import DoNotDisturbManager
from .dialog.presence import PreseneManager

from .nlp.disintegrator import Disintegrator
from .nlp.ner import NamedEntitiyRecognizer

from .notifier.between import Between
from .notifier.scheduler import Scheduler
from .notifier.skill_list import SkillList

from .bot.help import Guide
from .bot.worker import Worker

from .slack.resource import MsgResource
from .slack.slackbot import SlackerAdapter

from .skills.question import AttentionQuestion
from .skills.question import HappyQuestion

from .utils.data_loader import SkillDataLoader
from .utils.data_loader import SkillData
from .utils.logger import Logger
from .utils.logger import MessageLogger
from .utils.state import State


class MsgRouter:
    def __init__(self) -> None:
        self.logger = Logger().get_logger()
        self.msg_logger = MessageLogger().get_logger()

        self.dialog_manager = DialogManager()
        self.presence_manager = PreseneManager()
        self.dnd_manager = DoNotDisturbManager()

        self.f_runner = FunctionRunner()

    def presence_route(self, user: str = None, presence: str = None):
        """ Check Presence (Slack Users active/away)"""
        self.presence_manager.check_wake_up(presence)
        self.presence_manager.check_flow(presence)
        self.presence_manager.check_predictor(presence)

        State().presence_log(user, presence)
        self.logger.info(f"user: {user} presence: {presence}")

    def __on_flow(self):
        flow_classes = self.__make_flow_classes()
        route_class, behave, step_num = self.dialog_manager.get_flow(
            classes=flow_classes
        )

        self.logger.info(
            "From Flow - route to: "
            + route_class.__class__.__name__
            + ", "
            + str(behave)
        )

        getattr(route_class(slackbot=self.slackbot), behave)(
            step=step_num, params=self.text
        )

    def __make_flow_classes(self):
        return {
            "Between": Between,
            "Scheduler": Scheduler,
            "AttentionQuestion": AttentionQuestion,
            "HappyQuestion": HappyQuestion,
        }

    def dnd_route(self, user: str = None, dnd: dict = None):
        """ Check DND (Slack Do not disturb)"""

        # Do not disturb
        self.dnd_manager.call_is_holiday(dnd=dnd)

        self.logger.info(f"user: {user} dnd: {dnd}")

    def message_route(
        self,
        text: str = None,
        user: str = None,
        channel: str = None,
        direct: bool = False,
        webhook: bool = False,
    ):
        """ Check Message"""

        if text is not None:
            self.msg_logger.info(
                json.dumps({"channel": channel, "user": user, "text": text})
            )
            self.preprocessing(text)

        if Config.bot.ONLY_DIRECT is True and direct is False:
            # Skip
            return

        self.slackbot = SlackerAdapter(channel=channel, input_text=text, user=user)

        ner = NamedEntitiyRecognizer()

        # incomming-webhook
        if webhook:
            self.__on_relay(text)
            return

        # Check Flow
        if self.dialog_manager.is_on_flow():
            self.__on_flow()
            return

        # Check - help
        if self.dialog_manager.is_call_help(self.parsed_text):
            self.__call_help()
            return

        # Check - CRUD (Worker, Schedule, Between, FunctionManager)
        kino_keywords = {k: v["keyword"] for k, v in ner.kino.items()}
        classname = ner.parse(kino_keywords, self.parsed_text)

        if classname is not None:
            self.__call_CRUD(ner, classname)
            return

        # Check - skills
        skill_keywords = {k: v["keyword"] for k, v in ner.skills.items()}
        func_name = ner.parse(skill_keywords, self.parsed_text)
        if func_name is not None:
            self.__call_skills(func_name)
            self.__memory_predictor_skills()
            return

        # Check Memory
        if self.check_memory_skill():
            return

        self.logger.info("not understanding")

        random_num = random.randint(1, 100)
        if random_num > 60:
            guide = Guide(self.slackbot)
            guide.help_keyword()
        else:
            self.slackbot.send_message(text=MsgResource.NOT_UNDERSTANDING)

    def preprocessing(self, text: str):
        self.text = text

        split_pattern = NamedEntitiyRecognizer().SPLIT_PATTERN
        disintegrator = Disintegrator(text)
        self.parsed_text = disintegrator.convert2simple() + split_pattern + text

        self.logger.info("parsed input: " + self.parsed_text)

    def __on_relay(self, text: str):
        webhook = Webhook()
        webhook.relay(text)

    def check_memory_skill(self):
        classes = self.__make_memory_classes()
        route_class, func_name, params = self.dialog_manager.get_memory(classes=classes)

        route_class = route_class()
        f_params = self.f_runner.filter_f_params(self.parsed_text, func_name)
        if len(f_params) > 0:

            self.logger.info(
                "From Memory - route to: "
                + route_class.__class__.__name__
                + ", "
                + str(func_name)
            )

            getattr(route_class, func_name)(**f_params)
            return True
        else:
            return False

    def __make_memory_classes(self):
        return {"Functions": Functions}

    def __call_help(self):
        route_class = Guide(self.slackbot)
        behave = "help"
        self.logger.info(
            "route to: " + route_class.__class__.__name__ + ", " + str(behave)
        )
        getattr(route_class, behave)()

    def __call_CRUD(self, ner: str, classname: str):
        crud_classes = self.__make_crud_classes()
        route_class = crud_classes[classname](text=self.text, slackbot=self.slackbot)
        behave_ner = ner.kino[classname]["behave"]
        behave = ner.parse(behave_ner, self.parsed_text)

        self.logger.info(
            "route to: " + route_class.__class__.__name__ + ", " + str(behave)
        )
        getattr(route_class, behave)()

    def __make_crud_classes(self):
        return {
            "Between": Between,
            "Scheduler": Scheduler,
            "SkillList": SkillList,
            "Worker": Worker,
        }

    def __call_skills(self, func_name: str):
        if self.dialog_manager.is_toggl_timer(func_name):
            f_params = {"description": self.text[self.text.index("toggl") + 5 :]}
        else:
            f_params = self.f_runner.filter_f_params(self.parsed_text, func_name)

        state = State()
        state.memory_skill(self.text, func_name, f_params)
        self.logger.info(
            "From call skills - route to: " + func_name + ", " + str(f_params)
        )
        getattr(Functions(slackbot=self.slackbot), func_name)(**f_params)

    def __memory_predictor_skills(self):
        data_loader = SkillDataLoader()
        X = data_loader.make_X()[0]
        y = data_loader.make_y(self.text)
        if y is not None:
            skill_data = SkillData()
            skill_data.q.put_nowait((X, y))
