# -*- coding: utf-8 -*-

from .resource import MsgResource



class MsgTemplate:

    @staticmethod
    def make_schedule_template(pretext: str, data: dict) -> list:
        sorted(data.items())
        attachments = []
        for k, v in data.items():
            if k == "index":
                continue

            attachment = Attachement()

            if pretext == "":
                pass
            else:
                attachment.pretext = pretext

            if 'icon' in v:
                icon = v['icon']
                v.pop('icon', None)
            else:
                icon = MsgResource.TIMER_ICON

            attachment.title = icon + k + " " + \
                v['description'] + " : " + v['time_interval']
            del v['description']
            del v['time_interval']

            attachment.fallback = "알람 관련한 정보입니다. channel에서 확인하세요!"

            if 'color' in v:
                attachment.color = v['color']
                v.pop('color', None)

            fields = []
            if 'registered_alarm' in v:
                for d_k, d_v in v['registered_alarm'].items():
                    fields.append(Field(" - " + d_k, d_v, short="true"))

            attachment.fields = fields
            attachment.text = ""

            attachments.append(attachment)
        return attachments

    @staticmethod
    def make_skill_template(pretext: str, data: dict) -> list:
        sorted(data.items())
        attachments = []

        attachment = Attachement()
        if pretext == "":
            pass
        else:
            attachment.pretext = pretext

        attachment.fallback = "Function 관련 정보입니다. channel에서 확인하세요!"
        attachment.text = ""

        fields = []
        for f_name, f_detail in data.items():
            title = f_detail["icon"] + f_name
            text = MsgResource.ORANGE_DIAMOND_ICON + \
                f_detail['description'] + "\n"
            if len(f_detail['params']) != 0:
                text += MsgResource.ORANGE_DIAMOND_ICON + "params" + "\n"
                text += MsgResource.WHITE_ELEMENT_ICON + \
                    ", ".join(f_detail['params'])

            fields.append(Field(title, text, short="true"))
        attachment.fields = fields

        attachments.append(attachment)
        return attachments

    @staticmethod
    def make_help_template(guide: str, example: dict) -> list:
        attachments = []

        attachement = Attachement()
        attachement.pretext = ""
        attachement.title = MsgResource.ROBOT_ICON + MsgResource.GUIDE
        attachement.title_link = "https://github.com/DongjunLee/kino-bot"
        attachement.fallback = guide

        text = guide + "\n\n"
        for k, v in example.items():
            text += MsgResource.ORANGE_DIAMOND_ICON + k + ": " + v + "\n"
        attachement.text = text

        attachments.append(attachement)
        return attachments

    @staticmethod
    def make_giphy_template(q: str, url: str) -> list:
        attachments = []

        attachement = Attachement()
        attachement.title = q
        attachement.image_url = url
        attachement.fallback = "giphy: " + q
        attachement.mrkdwn_in = ["text", "pretext"]

        attachments.append(attachement)
        return attachments

    @staticmethod
    def make_weather_template(
            address: str,
            icon: str,
            summary: str,
            temperature=None,
            fallback="weather fallback") -> list:
        attachments = []

        attachement = Attachement()
        attachement.title = MsgResource.WEATHER
        attachement.fallback = MsgResource.WEATHER_ICONS(icon) + " " + fallback

        fields = []
        fields.append(Field("Address", address))
        fields.append(
            Field(
                "Sky Icon",
                MsgResource.WEATHER_ICONS(icon),
                short="true"))
        if temperature:
            fields.append(Field("Temperature", temperature, short="true"))
        fields.append(Field("Summary", summary))

        attachement.fields = fields

        attachments.append(attachement)
        return attachments

    @staticmethod
    def make_air_quality_template(station_name: str, data: dict) -> list:
        attachments = []

        cai = data['cai']

        attachement = Attachement()
        attachement.color = MsgResource.AIR_QUALITY_COLOR(cai['grade'])
        attachement.fallback = cai['description'] + " : " + cai['value']
        attachement.title = station_name + "의 대기질 정보 입니다."
        attachement.mrkdwn_in = ["text", "pretext"]

        fields = []
        fields.append(Field(cai['description'], cai['value'] + "점"))
        del data['cai']
        del data['pm25']

        for _, v in data.items():
            if isinstance(v, str):
                continue
            fields.append(
                Field(
                    v['description'],
                    v['value'] +
                    v['unit'] +
                    "\n" +
                    MsgResource.AIR_QUALITY_TEXT(
                        v['grade']),
                    short="true"))

        attachement.fields = fields

        attachments.append(attachement)
        return attachments

    @staticmethod
    def make_todoist_task_template(tasks: tuple) -> list:
        attachments = []

        fallback = "\n" + \
            "\n".join(
                list(map(lambda x: x[2] + ": " + x[1] + "(" + x[0] + ")", tasks)))
        for t in tasks:
            project_name, title, time, priority = t

            attachement = Attachement()
            attachement.title = "[" + project_name + "]: " + title
            attachement.fallback = fallback
            attachement.color = MsgResource.TODOIST_PRIORITY_COLOR(priority)

            text = MsgResource.CLOCK_ICON + " " + time
            attachement.text = text

            attachments.append(attachement)
        return attachments

    @staticmethod
    def make_feed_template(feed: tuple) -> list:
        attachments = []

        title, _, description = feed
        fallback = title + ": " + description

        attachement = Attachement()
        attachement.title = title
        attachement.fallback = fallback
        attachement.color = MsgResource.FEED_COLOR
        attachement.text = description

        attachments.append(attachement)
        return attachments

    @staticmethod
    def make_bus_stop_template(data: dict) -> list:
        attachments = []
        attachement = Attachement()
        attachement.fallback = "Bus 도착정보. "
        attachement.text = "Bus 도착정보 입니다."

        fields = []
        for k, v in data.items():
            title = MsgResource.BUS_ICON + str(k) + "번 버스"
            value = MsgResource.ORANGE_DIAMOND_ICON + \
                v['bus1'] + "\n" + MsgResource.ORANGE_DIAMOND_ICON + v['bus2']

            fields.append(Field(title, value, short="true"))
        attachement.fields = fields

        attachments.append(attachement)
        return attachments

    @staticmethod
    def make_summary_template(data: dict) -> list:
        attachments = []
        attachement = Attachement()

        attachement.color = data['Color']
        total_score = data['Total']
        del data['Color']
        del data['Total']

        attachement.fallback = "종합점수:  " + str(total_score)
        attachement.text = "종합점수 입니다."

        fields = []
        for k, v in data.items():
            fields.append(Field(k, str(v), short="true"))
        fields.append(Field("Total Score", str(total_score) + " 점"))

        attachement.fields = fields

        attachments.append(attachement)
        return attachments


class Attachement(dict):

    def __init__(self):
        self["color"] = "#438C56"
        self["mrkdwn_in"] = ["text", "pretext"]

    def __getattr__(self, name):
        if name in self:
            return self[name]
        else:
            raise AttributeError("No such attribute: " + name)

    def __setattr__(self, name, value):
        self[name] = value

    def __delattr__(self, name):
        if name in self:
            del self[name]
        else:
            raise AttributeError("No such attribute: " + name)


class Field(dict):

    def __init__(self, title, value, short="false"):
        self["title"] = title
        self["value"] = value
        self["short"] = short

    def __getattr__(self, name):
        if name in self:
            return self[name]
        else:
            raise AttributeError("No such attribute: " + name)

    def __setattr__(self, name, value):
        self[name] = value

    def __delattr__(self, name):
        if name in self:
            del self[name]
        else:
            raise AttributeError("No such attribute: " + name)


