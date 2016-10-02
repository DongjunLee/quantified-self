import re

from functions.manager import FunctionManager
from notifier.scheduler import Scheduler
from notifier.between import Between
from utils.state import State

class MsgRouter(object):

    def __init__(self):
        pass

    def route(self, msg):
        text = msg["text"]

        state = State()
        if state.is_do_something():
            route_class = globals()[state.current["class"]]()
            func_name = state.current["def"]
            step_num = state.current["step"]
            getattr(route_class, func_name)(step=step_num, params=text)
            return

        if text.startswith('알람'):
            re_list = self.__re_alarm_manager()
            route_class = Scheduler()
        elif text.startswith('시간대'):
            re_list = self.__re_between()
            route_class = Between()
        elif text.startswith('함수'):
            re_list = self.__re_function_table()
            route_class = FunctionManager()
        else:
            re_list = []
            route_class = object

        for re_dict in re_list:
            match_str, func_name = re_dict
            matcher = re.compile(match_str, re.I)
            result = matcher.match(msg["text"])

            if result:
                print("route to: " + route_class.__class__.__name__ + " method: " + func_name)
                getattr(route_class, func_name)()
                break

    def __re_alarm_manager(self):
        re_alarm_list = [
            (r'알람 등록', 'create'),
            (r'알람 보기', 'read'),
            (r'알람 변경', 'update'),
            (r'알람 삭제', 'delete'),
            (r'알람 시작', 'run'),
            (r'알람 중지', 'stop')
        ]
        return re_alarm_list

    def __re_between(self):
        re_between_list = [
            (r'시간대 등록', 'create'),
            (r'시간대 보기', 'read'),
            (r'시간대 변경', 'update'),
            (r'시간대 삭제', 'delete')
        ]
        return re_between_list

    def __re_function_table(self):
        re_function_table_list = [
            (r'함수 보기', 'read')
        ]
        return re_function_table_list
