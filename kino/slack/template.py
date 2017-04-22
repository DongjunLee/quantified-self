# -*- coding: utf-8 -*-

from .resource import MsgResource


class MsgTemplate(object):

    def __init__(self):
        pass

    def make_schedule_template(self, pretext, data):
        sorted(data.items())
        attachments = []
        for k, v in data.items():
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

            a_dict['title'] = icon + k + " " + \
                v['description'] + " : " + v['time_interval']
            del v['description']
            del v['time_interval']

            a_dict['fallback'] = "알람 관련한 정보입니다. channel에서 확인하세요!"

            if 'color' in v:
                a_dict['color'] = v['color']
                v.pop('color', None)
            else:
                a_dict['color'] = "#438C56"

            fields = []
            if 'registered_alarm' in v:
                for d_k, d_v in v['registered_alarm'].items():
                    field = {
                        "title": " - " + d_k,
                        "value": d_v,
                        "short": "true"
                    }
                    fields.append(field)

            a_dict['fields'] = fields
            a_dict['text'] = ""
            a_dict['mrkdwn_in'] = ["text", "pretext"]

            attachments.append(a_dict)
        return attachments

    def make_skill_template(self, pretext, data):
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

            text = MsgResource.ORANGE_DIAMOND_ICON + \
                f_detail['description'] + "\n"
            if len(f_detail['params']) != 0:
                text += MsgResource.ORANGE_DIAMOND_ICON + "params" + "\n"
                text += MsgResource.WHITE_ELEMENT_ICON + \
                    ", ".join(f_detail['params'])
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
        a_dict['title'] = MsgResource.ROBOT_ICON + MsgResource.GUIDE
        a_dict['fallback'] = "Kino에 대한 가이드입니다. channel에서 확인하세요!"
        a_dict['color'] = "#438C56"

        text = guide + "\n\n"
        for k, v in example.items():
            text += MsgResource.ORANGE_DIAMOND_ICON + k + ": " + v + "\n"
        a_dict['text'] = text

        a_dict['mrkdwn_in'] = ["text", "pretext"]

        attachments.append(a_dict)
        return attachments

    def make_weather_template(
            self,
            address,
            icon,
            summary,
            temperature=None,
            fallback="weather fallback"):
        attachments = []

        a_dict = {}
        a_dict['title'] = MsgResource.WEATHER
        a_dict['fallback'] = MsgResource.WEATHER_ICONS[icon] + " " + fallback
        a_dict['color'] = "#438C56"

        fields = []
        fields.append(self.field("Address", address))
        fields.append(
            self.field(
                "Sky Icon",
                MsgResource.WEATHER_ICONS[icon],
                short="true"))
        if temperature:
            fields.append(self.field("Temperature", temperature, short="true"))
        fields.append(self.field("Summary", summary))

        a_dict['fields'] = fields
        a_dict['mrkdwn_in'] = ["text", "pretext"]

        attachments.append(a_dict)
        return attachments

    def field(self, title, value, short="false"):
        return {"title": title, "value": value, "short": short}

    def make_air_quality_template(self, data):
        attachments = []

        cai = data['cai']

        a_dict = {}
        a_dict['color'] = MsgResource.AIR_QUALITY_COLOR(cai['grade'])
        a_dict['fallback'] = cai['description'] + " : " + cai['value']
        a_dict['title'] = "대기질 정보 입니다."
        a_dict['mrkdwn_in'] = ["text", "pretext"]

        fields = []
        field = {
            "title": cai['description'],
            "value": cai['value'] + "점"
        }
        fields.append(field)
        del data['cai']
        del data['pm25']

        for k, v in data.items():
            if isinstance(v, str):
                continue
            field = {}

            field['title'] = v['description']
            field['value'] = v['value'] + v['unit'] + "\n" + \
                MsgResource.AIR_QUALITY_TEXT(v['grade'])
            field['short'] = "true"
            fields.append(field)
        fields.append(field)

        a_dict['fields'] = fields

        attachments.append(a_dict)
        return attachments

    def make_todoist_task_template(self, tasks):
        attachments = []

        fallback = "\n" + \
            "\n".join(list(map(lambda x: x[2] + ": " + x[1] + "(" + x[0] + ")", tasks)))
        for t in tasks:
            project_name, title, time, priority = t

            a_dict = {}
            a_dict['title'] = "[" + project_name + "]: " + title
            a_dict['fallback'] = fallback
            a_dict['color'] = MsgResource.TODOIST_PRIORITY_COLOR(priority)

            text = MsgResource.CLOCK_ICON + " " + time
            a_dict['text'] = text
            a_dict['mrkdwn_in'] = ["text", "pretext"]

            attachments.append(a_dict)
        return attachments

    def make_bus_stop_template(self, data):
        attachments = []
        a_dict = {}
        a_dict['fallback'] = "Bus 도착정보. "
        a_dict['text'] = "Bus 도착정보 입니다."
        a_dict['mrkdwn_in'] = ["text", "pretext"]
        a_dict['color'] = "#438C56"

        fields = []
        for k, v in data.items():
            field = {}

            field['title'] = MsgResource.BUS_ICON + str(k) + "번 버스"
            field['value'] = MsgResource.ORANGE_DIAMOND_ICON + \
                v['bus1'] + "\n" + MsgResource.ORANGE_DIAMOND_ICON + v['bus2']
            field['short'] = "true"
            fields.append(field)
        a_dict['fields'] = fields

        attachments.append(a_dict)
        return attachments

    def make_summary_template(self, data):
        attachments = []
        a_dict = {}

        a_dict['color'] = data['Color']
        total_score = data['Total']
        del data['Color']
        del data['Total']

        a_dict['fallback'] = "종합점수:  " + str(total_score)
        a_dict['text'] = "종합점수 입니다."
        a_dict['mrkdwn_in'] = ["text", "pretext"]

        fields = []
        for k, v in data.items():
            field = {}

            field['title'] = k
            field['value'] = str(v)
            field['short'] = "true"
            fields.append(field)

        field = {
            "title": "Total Score",
            "value": str(total_score) + " 점"
        }
        fields.append(field)

        a_dict['fields'] = fields

        attachments.append(a_dict)
        return attachments
