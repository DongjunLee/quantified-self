# -*- coding: utf-8 -*-

from utils.resource import MessageResource

class MsgTemplate(object):

    def __init__(self):
        pass

    def make_schedule_template(self, pretext, data):
        attachments = []
        for k,v in data.items():
            if k == "index":
                continue

            a_dict = {}

            if pretext == "":
                pass
            else:
                a_dict['pretext'] = pretext

            a_dict['title'] = "시간대. " + MessageResource.TIMER_ICON + k + " " + v['description']
            del v['description']

            a_dict['fallback'] = "알람 관련한 정보입니다. channel에서 확인하세요!"

            if 'color' in v:
                a_dict['color'] = v['color']
                v.pop('color', None)
            else:
                a_dict['color'] = "#438C56"

            text = ""
            for d_k,d_v in v.items():
                if type(d_v) == type([]):
                    text += MessageResource.ORANGE_DIAMOND_ICON + d_k + "\n"
                    for element in d_v:
                        text += MessageResource.WHITE_ELEMENT_ICON + element + "\n"
                else:
                    text += MessageResource.ORANGE_DIAMOND_ICON + d_k + ": " + d_v + "\n"
            a_dict['text'] = text

            a_dict['mrkdwn_in'] = ["text", "pretext"]

            attachments.append(a_dict)
        return attachments

    def make_function_template(self, pretext, data):
        attachments = []
        for f_name, f_detail in data.items():

            a_dict = {}
            if pretext == "":
                pass
            else:
                a_dict['pretext'] = pretext

            a_dict['title'] = f_detail["icon"] + f_name
            a_dict['fallback'] = "Function 관련 정보입니다. channel에서 확인하세요!"
            a_dict['color'] = "#438C56"

            text = MessageResource.ORANGE_DIAMOND_ICON + "description: " + f_detail['description'] + "\n"
            text += MessageResource.ORANGE_DIAMOND_ICON + "params" + "\n"
            text += MessageResource.WHITE_ELEMENT_ICON + ", ".join(f_detail['params'])
            a_dict['text'] = text

            a_dict['mrkdwn_in'] = ["text", "pretext"]

            attachments.append(a_dict)
        return attachments

    def make_help_template(self, guide, example):
        attachments = []

        a_dict = {}
        a_dict['pretext'] = ""
        a_dict['title'] = MessageResource.ROBOT_ICON + MessageResource.GUIDE
        a_dict['fallback'] = "Kino에 대한 가이드입니다. channel에서 확인하세요!"
        a_dict['color'] = "#438C56"

        text = guide + "\n\n"
        for k,v in example.items():
            text += MessageResource.ORANGE_DIAMOND_ICON + k + ": " + v + "\n"
        a_dict['text'] = text

        a_dict['mrkdwn_in'] = ["text", "pretext"]

        attachments.append(a_dict)
        return attachments

    def make_weather_template(self, address, icon, summary, temperature=None):
        attachments = []

        a_dict = {}
        a_dict['title'] = MessageResource.WEATHER
        a_dict['fallback'] = "날씨 관련 정보입니다. channel에서 확인하세요!"
        a_dict['color'] = "#438C56"

        text = address + " 의 "
        if temperature is None:
            text += "오늘의 날씨는 "
        else:
            text += "현재 날씨는 " + "{:.3}".format(temperature) + "도에 "
        text += "\n" + MessageResource.WEATHER_ICONS[icon] + " " + summary + " 입니다."
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
            a_dict['color'] = MessageResource.TODOIST_PRIORITY_COLOR(priority)

            text = MessageResource.CLOCK_ICON + " " + time + " " + MessageResource.TODOIST_TIME
            a_dict['text'] = text
            a_dict['mrkdwn_in'] = ["text", "pretext"]

            attachments.append(a_dict)
        return attachments
