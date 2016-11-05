# -*- coding: utf-8 -*-

from slack import MsgResource

class MsgTemplate(object):

    def __init__(self):
        pass

    def make_schedule_template(self, pretext, data):
        sorted(data.items())
        attachments = []
        for k,v in data.items():
            if k == "index":
                continue

            a_dict = {}

            if pretext == "":
                pass
            else:
                a_dict['pretext'] = pretext

            if 'icon' in v:
                icon = v['icon']
                v.pop('icon', None)
            else:
                icon = MsgResource.TIMER_ICON

            a_dict['title'] = icon + k + " " + v['description'] + " : " + v['time_interval']
            del v['description']
            del v['time_interval']

            a_dict['fallback'] = "알람 관련한 정보입니다. channel에서 확인하세요!"

            if 'color' in v:
                a_dict['color'] = v['color']
                v.pop('color', None)
            else:
                a_dict['color'] = "#438C56"

            text = ""
            for d_k,d_v in v.items():
                if type(d_v) == type([]):
                    text += MsgResource.ORANGE_DIAMOND_ICON + d_k + "\n"
                    for element in d_v:
                        text += MsgResource.WHITE_ELEMENT_ICON + element + "\n"
                else:
                    text += MsgResource.ORANGE_DIAMOND_ICON + d_k + ": " + d_v + "\n"
            a_dict['text'] = text

            a_dict['mrkdwn_in'] = ["text", "pretext"]

            attachments.append(a_dict)
        return attachments

    def make_function_template(self, pretext, data):
        sorted(data.items())
        attachments = []
        a_dict = {}
        if pretext == "":
            pass
        else:
            a_dict['pretext'] = pretext

        a_dict['fallback'] = "Function 관련 정보입니다. channel에서 확인하세요!"
        a_dict['text'] = ""
        a_dict['mrkdwn_in'] = ["text", "pretext"]
        a_dict['color'] = "#438C56"

        fields = []
        for f_name, f_detail in data.items():
            field = {}

            field['title'] = f_detail["icon"] + f_name

            text = MsgResource.ORANGE_DIAMOND_ICON + "description: " + f_detail['description'] + "\n"
            text += MsgResource.ORANGE_DIAMOND_ICON + "params" + "\n"
            text += MsgResource.WHITE_ELEMENT_ICON + ", ".join(f_detail['params'])
            field['value'] = text
            field['short'] = "true"
            fields.append(field)
        a_dict['fields'] = fields

        attachments.append(a_dict)
        return attachments

    def make_help_template(self, guide, example):
        attachments = []

        a_dict = {}
        a_dict['pretext'] = ""
        a_dict['title'] = MsgResource.ROBOT_ICON + MessageResource.GUIDE
        a_dict['fallback'] = "Kino에 대한 가이드입니다. channel에서 확인하세요!"
        a_dict['color'] = "#438C56"

        text = guide + "\n\n"
        for k,v in example.items():
            text += MsgResource.ORANGE_DIAMOND_ICON + k + ": " + v + "\n"
        a_dict['text'] = text

        a_dict['mrkdwn_in'] = ["text", "pretext"]

        attachments.append(a_dict)
        return attachments

    def make_weather_template(self, address, icon, summary, temperature=None):
        attachments = []

        a_dict = {}
        a_dict['title'] = MsgResource.WEATHER
        a_dict['fallback'] = "날씨 관련 정보입니다. channel에서 확인하세요!"
        a_dict['color'] = "#438C56"

        text = address + " 의 "
        if temperature is None:
            text += "오늘의 날씨는 "
        else:
            text += "현재 날씨는 " + "{:.3}".format(temperature) + "도에 "
        text += "\n" + MsgResource.WEATHER_ICONS[icon] + " " + summary + " 입니다."
        a_dict['text'] = text

        a_dict['mrkdwn_in'] = ["text", "pretext"]

        attachments.append(a_dict)
        return attachments


    def make_todoist_task_template(self, tasks):
        attachments = []

        for t in tasks:
            project_name, title, time, priority = t

            a_dict = {}
            a_dict['title'] = project_name + ": " + title
            a_dict['fallback'] = "일정 관련 정보입니다. channel에서 확인하세요!"
            a_dict['color'] = MsgResource.TODOIST_PRIORITY_COLOR(priority)

            text = MsgResource.CLOCK_ICON + " " + time + " " + MsgResource.TODOIST_TIME
            a_dict['text'] = text
            a_dict['mrkdwn_in'] = ["text", "pretext"]

            attachments.append(a_dict)
        return attachments
