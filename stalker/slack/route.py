import re

from alarm_manager.alarm_manager import AlarmManager

class MsgRouter(object):

    def __init__(self, msg):
        self.msg = msg

    def route(self):
        text = self.msg["text"]

        if text.startswith( '알람'):
            self.__route__alarm_manager()

    def __route__alarm_manager(self):

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
            result = matcher.match(self.msg["text"])

            if result:
                getattr(alarm_manager, func_name)(result.groups())
                break
