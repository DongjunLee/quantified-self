# -*- coding: utf-8 -*-

import random
import re
import time

from .background import schedule

from .nlp.ner import NamedEntitiyRecognizer

from .skills.feed import FeedNotifier
from .skills.humor import Humor
from .skills.summary import Summary

from .slack.slackbot import SlackerAdapter
from .slack.resource import MsgResource

from .utils.arrow import ArrowUtil
from .utils.data_handler import DataHandler
from .utils.logger import Logger
from .utils.member import Member



class Functions(object):

    def __init__(self, slackbot=None):
        self.data_handler = DataHandler()
        self.registered = RegisteredFuctions().list

        if slackbot is None:
            self.slackbot = SlackerAdapter()
        else:
            self.slackbot = slackbot

    def check_go_to_bed(self):
        summary = Summary()
        summary.check_go_to_bed()
        summary.check_commit_count()

        self.data_handler.edit_cache(("feed_links", []))

    def feed_notify(self):
        feed_notifier = FeedNotifier()
        feed_notifier.notify_all()

    def humor(self):
        """
        keyword: [["재밌는", "이야기"], ["개그"]]
        description: "Korea Azae Humor (using [honeyjam](https://github.com/DongjunLee/honeyjam))."
        icon: ":smile_cat: "
        """

        humor = Humor()
        question, answer = humor.honeyjam()
        
        self.slackbot.send_message(text=MsgResource.HUMOR_QUESTION(question=question))

        time.sleep(2)
        self.slackbot.send_message(text=MsgResource.HUMOR_ANSWER(answer=answer))

        haha_num = random.randint(1, 5)
        self.slackbot.send_message(text=MsgResource.HUMOR_END(haha_num))

        sorry_index = random.randint(1, 100)
        if sorry_index < 25:
            time.sleep(1)
            self.slackbot.send_message(text=MsgResource.HUMOR_SORRY)

    def send_message(self, text: str=None):
        """
        keyword: []
        description: "Send a text message."
        icon: ":speech_balloon: "
        """

        self.slackbot.send_message(text=text)



class RegisteredFuctions(object):
    class __List:
        def __init__(self):
            self.list = DataHandler().read_file("skills.json")

    instance = None

    def __init__(self):
        if not RegisteredFuctions.instance:
            RegisteredFuctions.instance = RegisteredFuctions.__List()

    def __getattr__(self, name):
        return getattr(self.instance, name)


class FunctionRunner(object):

    def __init__(self, text=None):
        self.input = text
        self.functions = Functions().registered
        self.logger = Logger().get_logger()

    def load_function(
            self,
            start_time=None,
            end_time=None,
            func_name=None,
            params=None,
            repeat=False,
            day_of_week=None,
            not_holiday=False):

        if not_holiday and Summary().is_holiday():
            return

        if not ArrowUtil.is_today_day_of_week(day_of_week):
            return

        if not repeat:
            self.__excute(func_name, params)
            return schedule.CancelJob
        elif (repeat) and (ArrowUtil.is_between(start_time, end_time)):
            self.__excute(func_name, params)

    def __excute(self, func_name, params):
        self.logger.info(
            "load_function: " +
            str(func_name) +
            ", " +
            str(params))
        getattr(Functions(), func_name)(**params)

    def filter_f_params(self, text, func_name):
        ner = NamedEntitiyRecognizer()

        func_param_list = ner.skills[func_name]['params']
        params = {k: ner.parse(v, text) for k, v in ner.params.items()}

        member = Member()
        member_name = member.get_names(text)
        params["member"] = member_name

        f_params = {}
        if params is not None:
            for k, v in params.items():
                if k in func_param_list and v is not None:
                    f_params[k] = v
        return f_params
