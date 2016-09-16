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
            ('알람등록 (.*)', 'create'),
            (r'알람보기', 'read'),
            ('알람변경 (.*)', 'update'),
            ('알람삭제 (.*)', 'delete')
        ]

        for re_alarm in re_alarm_list:
            match_str, func_name = re_alarm
            matcher = re.compile(match_str, re.I)
            result = matcher.match(msg["text"])

            if result:
                getattr(alarm_manager, func_name)(result.groups())
                break
