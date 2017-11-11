# -*- coding: utf-8 -*-

import random
import re
import time

from .background import schedule

from .nlp.ner import NamedEntitiyRecognizer

from .skills.bus import Bus
from .skills.card import BusinessCard
from .skills.feed import FeedNotifier
from .skills.github import GithubManager
from .skills.humor import Humor
from .skills.maxim import Maxim
from .skills.naver import Naver
from .skills.question import AttentionQuestion
from .skills.question import HappyQuestion
from .skills.rescue_time import RescueTime
from .skills.samhangsi.generator import SamhangSiGenerator
from .skills.summary import Summary
from .skills.todoist import TodoistManager
from .skills.toggl import TogglManager
from .skills.trello import TrelloManager
from .skills.weather import Weather

from .slack.slackbot import SlackerAdapter
from .slack.resource import MsgResource

from .utils.arrow import ArrowUtil
from .utils.data_handler import DataHandler
from .utils.data_loader import SkillData
from .utils.data_loader import FeedData
from .utils.logger import Logger
from .utils.member import Member



class Functions(object):

    IDEA_LIST = "Inbox"
    KANBAN_TASKS = "Tasks"
    KANBAN_DOING = "Doing"
    KANBAN_DONE = "Done"
    KANBAN_BREAK = "Break"

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

        self._reset_data()

    def _reset_data(self):
        self.data_handler.edit_cache(("feed_links", []))
        FeedData().reset()
        SkillData().reset()

    def feed_notify(self):
        feed_notifier = FeedNotifier()
        feed_notifier.notify_all()

    def air_quality(self):
        """
        keyword: ["공기질", "미세먼지", "air quality"]
        description: "Air quality forecast. (can use only Korea [airkoreaPy](https://github.com/DongjunLee/airkoreaPy))"
        icon: ":factory: "
        """

        weather = Weather(slackbot=self.slackbot)
        weather.air_quality()

    def attention_question(self, text: str=None):
        """
        keyword: [["집중도", "조사"], ["집중도", "확인"], ["attention", "question"]]
        description: "Attention survey after do task."
        icon: ":writing_hand: "
        """

        attention = AttentionQuestion(slackbot=self.slackbot)
        attention.question()

    def attention_report(self, timely: str="daily"):
        """
        keyword: [["집중도", "리포트"], ["attention", "report"]]
        description: "Attention Report."
        icon: ":writing_hand: "
        """

        if timely is None:
            timely = 'daily'
        attention = AttentionQuestion(slackbot=self.slackbot)
        attention.report(timely=timely)

    def bus_stop(self, station_id: str=None, real_time: str=None):
        """
        keyword: [["버스", "도착"], ["버스", "언제"], ["버스", "조회"]]
        description: "Bus arrival information. (can use only Korea (gbus api))"
        icon: ":oncoming_bus: "
        """

        if real_time is None:
            real_time = False
        bus = Bus(slackbot=self.slackbot)
        bus.arrive_info(station_id, real_time=real_time)

    def forecast(self, timely: str="current"):
        """
        keyword: ["날씨", "예보", "weather", "forecast"]
        description: "Weather forecast. (using [darksky](https://darksky.net/))"
        icon: ":sun_with_face: "
        """

        if timely is None:
            timely = 'current'
        weather = Weather(slackbot=self.slackbot)
        weather.forecast(timely=timely)

    def github_commit(self, timely: str="daily"):
        """
        keyword: ["커밋", "commit", "깃헙", "github"]
        description: "Check [Github](https://github.com) push count."
        icon: ":octocat: "
        """

        if timely is None:
            timely = 'daily'
        github = GithubManager(slackbot=self.slackbot)
        github.commit(timely=timely)

    def happy_question(self):
        """
        keyword: [["행복도", "조사"], ["행복도", "확인"], ["happy", "question"]]
        description: "Happiness survey."
        icon: ":smile: "
        """

        happy = HappyQuestion(slackbot=self.slackbot)
        happy.question()

    def happy_report(self, timely: str="daily"):
        """
        keyword: [["행복도", "리포트"], ["happy", "report"]]
        description: "Happiness Report."
        icon: ":smile: "
        """

        if timely is None:
            timely = 'daily'
        happy = HappyQuestion(slackbot=self.slackbot)
        happy.report(timely=timely)

    def honeyjam(self):
        """
        keyword: [["재밌는", "이야기"], ["개그"]]
        description: "**Easter Egg** - Korea Azae Humor (using [honeyjam](https://github.com/DongjunLee/honeyjam))."
        icon: ":honey_pot: "
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

    def jenkins_build(self, job_name: str=None, branch: str=None):
        """
        keyword: ["배포", "deploy"]
        description: "Build a registered project for Jenkins."
        icon: ":building_construction: "
        """

        jenkins = JenkinsClient()
        jenkins.build(job_name, branch)

    def kanban_sync(self):
        """
        keyword: [["칸반", "싱크"], ["kanban", "sync"]]
        description: "Todoist's tasks and Kanban board's card Syncing."
        icon: ":clipboard: "
        """

        self.slackbot.send_message(text=MsgResource.KANBAN_SYNC)

        todoist = TodoistManager(slackbot=self.slackbot)
        today_label_tasks = todoist.get_tasks_with_overdue_and_label()

        trello = TrelloManager()

        task_list = trello.get_list_by_name(self.KANBAN_TASKS)
        task_list.archive_all_cards()

        for task in today_label_tasks:
            card_name = task['label'] + " - " + task['content']
            task_list.add_card(re.sub(r" \d+분", "", card_name))

    def keep_idea(self, hashtag: str=None):
        """
        keyword: [["keep", "idea"], ["킵", "아이디어"], ["아이디어", "저장"], ["아이디어", "기억"]]
        description: "Keep idea in Trello board's inbox list."
        icon: ":thinking_face: "
        """

        if hashtag is None:
            self.slackbot.send_message(text=MsgResource.HASHTAG_NOT_FOUND)
            return

        trello = TrelloManager()
        trello.add_card(self.IDEA_LIST, hashtag)

        self.slackbot.send_message(text=MsgResource.ADD_IDEA)

    def maxim_nietzsche(self):
        """
        keyword: [["니체", "명언"], ["nietzsche", "maxim"]]
        description: "Nietzsche's Maxim."
        icon: ":scales: "
        """

        maxim = Maxim(slackbot=self.slackbot)
        maxim.nietzsche()

    def remind_idea(self):
        """
        keyword: [["remind", "idea"], ["리마인드", "아이디어"]]
        description: "Remind Trello's inbox card randomly pick."
        icon: ":thinking_face: "
        """

        trello = TrelloManager()
        idea = trello.get_random_card_name()
        if idea is None:
            self.slackbot.send_message(text=MsgResource.EMPTY_IDEA)
        else:
            self.slackbot.send_message(text=MsgResource.REMIND_IDEA(idea=idea))

    def rescuetime_efficiency(self, timely: str="daily"):
        """
        keyword: ["레스큐타임 효율성", "작업 효율", "생산성 차트", ["rescuetime", "chart"]]
        description: "RescueTime Efficiency Chart"
        icon: ":chart_with_upwards_trend: "
        """

        if timely is None:
            timely = 'daily'
        rescuetime = RescueTime(slackbot=self.slackbot)
        rescuetime.efficiency(timely=timely)

    def samhangsi(self, samhangsi_tag: str=None):
        """
        keyword: ["삼행시"]
        description: "I am thinking about the Samhangsi with the kor ballad! (using [char-rnn-tensorflow](https://github.com/DongjunLee/char-rnn-tensorflow))"
        icon: ":musical_score: "
        """

        word = samhangsi_tag[1:]
        non_hangul = re.findall('[^ ㄱ-ㅣ가-힣]+', word)
        if len(non_hangul) > 0:
            self.slackbot.send_message(text=MsgResource.SAMHANGSI_ONLY_KOR)
            return

        self.slackbot.send_message(text=MsgResource.SAMHANGSI_PREPARE(word=word))

        generator = SamhangSiGenerator()
        generator.load_model()

        result = generator.generate(word)
        self.slackbot.send_message(text=result)

    def send_message(self, text: str=None):
        """
        keyword: []
        description: "Send a text message."
        icon: ":speech_balloon: "
        """

        self.slackbot.send_message(text=text)

    def today_briefing(self):
        """
        keyword: [["하루", "브리핑"], ["오늘하루", "브리핑"], ["today", "briefing"]]
        description: "Today Briefing - brief Todoist tasks"
        icon: ":city_sunset: "
        """

        todoist = TodoistManager(slackbot=self.slackbot)
        todoist.schedule()

    def today_summary(self, timely: str=None):
        """
        keyword: [["하루", "마무리"], ["하루", "요약"], ["today", "summary"]]
        description: "Today summary - **todoist_feedback**, **toggl_report**, **rescuetime_efficiency**, **happy_report**, **attention_report**, **github_commit**"
        icon: ":night_with_stars: "
        """

        self.slackbot.send_message(text=MsgResource.TODAY_SUMMARY)
        self.todoist_feedback()
        self.toggl_report(timely=timely)
        self.rescuetime_efficiency(timely=timely)
        self.happy_report(timely=timely)
        self.attention_report(timely=timely)
        self.github_commit(timely=timely)

    def todoist_feedback(self):
        """
        keyword: [["할일", "피드백"], ["todoist", "feedback"]]
        description: "Feedback from Todoist activity."
        icon: ":memo: "
        """

        todoist = TodoistManager(slackbot=self.slackbot)
        todoist.feedback()

    def todoist_remain(self):
        """
        keyword: [["남은", "작업"], ["remain", "task"]]
        description: "Show todoist's remaining tasks."
        icon: ":page_with_curl: "
        """

        todoist = TodoistManager(slackbot=self.slackbot)
        todoist.remain_task()

    def toggl_checker(self):
        """
        keyword: [["작업", "시간"], ["시간", "체크"], ["task", "time", "check"]]
        description: "Toggl time checker Every 30 minutes."
        icon: ":bell: "
        """

        toggl = TogglManager(slackbot=self.slackbot)
        toggl.check_toggl_timer()

    def toggl_report(self, kind: str="chart", timely: str="daily"):
        """
        keyword: [["작업", "리포트"], ["task", "report"]]
        description: "Toggl task Report."
        icon: ":bar_chart: "
        """

        if kind is None:
            kind = 'chart'
        if timely is None:
            timely = 'daily'
        toggl = TogglManager(slackbot=self.slackbot)
        toggl.report(kind=kind, timely=timely)

    def toggl_timer(self, description: str=None):
        """
        keyword: ["toggl"]
        description: "Toggl Timer."
        icon: ":watch: "
        """

        toggl = TogglManager(slackbot=self.slackbot)
        toggl.timer(description=description)

    def total_chart(self):
        """
        keyword: [["종합", "차트"], ["overall", "chart"], ["total", "chart"]]
        description: "Overall chart - weekly productivity, happiness, overall score chart."
        icon: ":chart: "
        """

        summary = Summary(slackbot=self.slackbot)
        summary.total_chart()

    def total_score(self):
        """
        keyword: [["종합", "점수"], ["overall", "score"], ["total", "score"]]
        description: "Overall score  - Productivity (RescueTime, Github Commit, Todoist, Toggl), Mean happiness, mean attention, Exercise, Diary."
        icon: ":chart: "
        """

        summary = Summary(slackbot=self.slackbot)
        summary.total_score()

    def translate(self, english: str="", source: str="en", target: str="ko"):
        """
        keyword: ["번역", "translate"]
        description: "Language translation using [Naver Papago api](https://developers.naver.com/docs/nmt/reference/)."
        icon: ":crystal_ball: "
        """

        if source is None:
            source = "en"
        if target is None:
            target = "ko"
        naver = Naver(slackbot=self.slackbot)
        naver.translate(english, source=source, target=target)



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
