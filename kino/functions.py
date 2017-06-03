# -*- coding: utf-8 -*-

from .core import schedule

from .nlp.ner import NamedEntitiyRecognizer

from .skills.bus import Bus
from .skills.github import GithubManager
from .skills.maxim import Maxim
from .skills.naver import Naver
from .skills.question import AttentionQuestion
from .skills.question import HappyQuestion
from .skills.rescue_time import RescueTime
from .skills.summary import Summary
from .skills.todoist import TodoistManager
from .skills.toggl import TogglManager
from .skills.trello import TrelloManager
from .skills.weather import Weather

from .slack.resource import MsgResource
from .slack.slackbot import SlackerAdapter

from .utils.arrow import ArrowUtil
from .utils.data_handler import DataHandler
from .utils.logger import Logger



class Functions(object):

    def __init__(self):
        self.data_handler = DataHandler()
        self.slackbot = SlackerAdapter()
        self.registered = RegisteredFuctions().list

    def check_go_to_bed(self):
        summary = Summary()
        summary.check_go_to_bed()
        summary.check_commit_count()

    def send_message(self, text=None):
        self.slackbot.send_message(text=text)

    def bus_stop(self, station_id=None, real_time=None):
        if real_time is None:
            real_time = False
        bus = Bus()
        bus.arrive_info(station_id, real_time=real_time)

    def forecast(self, timely="current"):
        if timely is None:
            timely = 'current'
        weather = Weather()
        weather.forecast(timely=timely)

    def air_quality(self):
        weather = Weather()
        weather.air_quality()

    def attention_question(self, text=None):
        attention = AttentionQuestion()
        attention.question()

    def attention_report(self, timely="daily"):
        if timely is None:
            timely = 'daily'
        attention = AttentionQuestion()
        attention.report(timely=timely)

    def github_commit(self, timely="daily"):
        if timely is None:
            timely = 'daily'
        github = GithubManager()
        github.commit(timely=timely)

    def happy_question(self):
        happy = HappyQuestion()
        happy.question()

    def happy_report(self, timely="daily"):
        if timely is None:
            timely = 'daily'
        happy = HappyQuestion()
        happy.report(timely=timely)

    def total_score(self):
        summary = Summary()
        summary.total_score()

    def total_chart(self):
        summary = Summary()
        summary.total_chart()

    def translate(self, english="", source="en", target="ko"):
        if source is None:
            source = "en"
        if target is None:
            target = "ko"
        naver = Naver()
        naver.translate(english, source=source, target=target)

    def rescuetime_efficiency(self, timely="daily"):
        if timely is None:
            timely = 'daily'
        rescuetime = RescueTime()
        rescuetime.efficiency(timely=timely)

    def today_briefing(self):
        todoist = TodoistManager()
        todoist.schedule()

    def today_summary(self, timely=None):
        self.slackbot.send_message(text=MsgResource.TODAY_SUMMARY)
        self.todoist_feedback()
        self.toggl_report(timely=timely)
        self.rescuetime_efficiency(timely=timely)
        self.attention_report(timely=timely)
        self.github_commit(timely=timely)

    def kanban_init(self):
        todoist = TodoistManager()
        todoist.auto_update_tasks()

        today_label_tasks = todoist.get_today_tasks_with_label()
        trello = TrelloManager()
        trello.clean_board()

        task_list = trello.get_list_by_name('Tasks')
        for task in today_label_tasks:
            task_list.add_card(task['label'] + " - " + task['content'])

    def todoist_feedback(self):
        todoist = TodoistManager()
        todoist.feedback()

    def todoist_remain(self):
        todoist = TodoistManager()
        todoist.remain_task()

    def toggl_timer(self, description=None):
        toggl = TogglManager()
        toggl.timer(description=description)

    def toggl_checker(self):
        toggl = TogglManager()
        toggl.check_toggl_timer()

    def toggl_report(self, kind="chart", timely="daily"):
        if kind is None:
            kind = 'chart'
        if timely is None:
            timely = 'daily'
        toggl = TogglManager()
        toggl.report(kind=kind, timely=timely)

    def maxim_nietzsche(self):
        maxim = Maxim()
        maxim.nietzsche()


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
            not_holiday=False):

        if not_holiday and Summary().is_holiday():
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

        f_params = {}
        if params is not None:
            for k, v in params.items():
                if k in func_param_list:
                    f_params[k] = v
        return f_params
