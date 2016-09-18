import re

from alarm_manager.alarm_manager import AlarmManager

class MsgRouter(object):

    def __init__(self):
        pass

    def route(self, msg):
        text = msg["text"]

        if text.startswith( '알람'):
            self.__route__alarm_manager(msg)

    def __route__alarm_manager(self, msg):

        alarm_manager = AlarmManager()

        re_alarm_list = [
            (r'알람 등록 (.*)', 'create'),
            (r'알람간격 등록 (.*)', 'create_between'),
            (r'알람 보기', 'read'),
            (r'알람간격 보기', 'read_between'),
            (r'알람 변경 (.*)', 'update'),
            (r'알람간격 변경 (.*)', 'update_between'),
            (r'알람 삭제 (.*)', 'delete'),
            (r'알람간격 삭제 (.*)', 'delete_between'),
            (r'알람 시작', 'run_schedule'),
            (r'알람 중지', 'stop_schedule')
        ]

        for re_alarm in re_alarm_list:
            match_str, func_name = re_alarm
            matcher = re.compile(match_str, re.I)
            result = matcher.match(msg["text"])

            if result:
                print("route to: " + func_name)
                getattr(alarm_manager, func_name)(result.groups())
                break
