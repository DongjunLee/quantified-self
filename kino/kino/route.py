import re

from functions.manager import FunctionManager
from functions.weather import Weather
from functions.youtube_downloader import YoutubeDownloader
from functions.todoist import TodoistManager
from kino.disintegrator import Disintegrator
from kino.help import Guide
from kino.worker import Worker
from notifier.scheduler import Scheduler
from notifier.between import Between
from slack.slackbot import SlackerAdapter
from utils.logger import Logger
from utils.state import State
from utils.resource import MessageResource

class MsgRouter(object):

    def __init__(self):
        self.disintegrator = Disintegrator()
        self.state = State()
        self.slackbot = SlackerAdapter()
        self.logger = Logger().get_logger()

    def route(self, text=None, user=None):

        if self.state.is_do_something():
            current_state = self.state.current
            route_class, func_name, step_num = self.__to_state_next_step(current_state)
            getattr(route_class, func_name)(step=step_num, params=text)
            return

        simple_text = self.disintegrator.convert2simple(sentence=text)

        self.logger.info("input: " + simple_text)

        is_greeting = self.__greeting_call_bot(simple_text)
        route_class = self.__parse_route_class(simple_text)
        func_name = self.__parse_func_name(simple_text)

        self.logger.info("route to: " + route_class.__class__.__name__ + " method: " + func_name)
        if func_name == "help":
            route_class = Guide()
            getattr(route_class, func_name)()
        elif func_name == "make_link":
            getattr(route_class, func_name)(params=text)
        elif (route_class == None or func_name == "not exist") and is_greeting:
            pass
        elif route_class == None or func_name == "not exist":
            self.slackbot.send_message(text=MessageResource.NOT_UNDERSTANDING)
        else:
            getattr(route_class, func_name)()

    def __to_state_next_step(self, current_state):
        route_class = globals()[current_state["class"]]()
        func_name = current_state["def"]
        step_num = current_state["step"]
        return route_class, func_name, step_num

    def __greeting_call_bot(self, text):
        if "키노" in text or "kino" in text:
            self.slackbot.send_message(text="저를 찾으셨나요!^^ 무엇을 도와드릴까요?")
            return True
        return False

    def __parse_route_class(self, text):
        route_class_list = [
            ('일', Worker()),
            ('알람', Scheduler()),
            ('시간대', Between()),
            ('함수', FunctionManager()),
            ('날씨', Weather()),
            ('할일', TodoistManager()),
            ('youtu.be', YoutubeDownloader()),
            ('youtube.com', YoutubeDownloader())
        ]

        for route_class in route_class_list:
            if route_class[0] in text:
                return route_class[1]
        return None

    def __parse_func_name(self, text):
        func_name_pair_list = [
            (['도움말'], 'help'),
            (['등록', '추가'], 'create'),
            (['보다', '보기', '보이다',' 알다', '어떻다'], 'read'),
            (['삭제', '제거', '없애다'], 'delete'),
            (['시작', '하다', '하자'], 'run'),
            (['중지', '멈추다', '그만'], 'stop'),
            (['브리핑'], 'today_briefing'),
            (['youtu.be', 'youtube.com'], 'make_link')
        ]

        for func_name_pair in func_name_pair_list:
            func_pattern_list, func_name = func_name_pair
            if any([p for p in func_pattern_list if p in text]):
                return func_name
        return "not exist"
