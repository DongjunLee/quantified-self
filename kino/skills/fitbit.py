#!/usr/bin/env python

import fitbit
from hbconfig import Config

from kino.slack.slackbot import SlackerAdapter
from kino.utils.data_handler import DataHandler


class Fitbit:

    def __init__(self, slackbot=None):
        self.api = fitbit.api.Fitbit(
            Config.open_api.fitbit.CLIENT_ID,
            Config.open_api.fitbit.CLIENT_SECRET,
            access_token=Config.open_api.fitbit.ACCESS_TOKEN,
            refresh_token="<refresh>",
        )
        self.data_handelr = DataHandler()

        if slackbot is None:
            self.slackbot = SlackerAdapter(
                channel=Config.slack.channel.get("REPORT", "#general")
            )
        else:
            self.slackbot = slackbot

    def get_sleeps(self):
        sleep_data = self.api.sleep()

        datas = []
        for s in sleep_data["sleep"]:
            data = {
                "is_main": s["isMainSleep"],
                "start_time": s["startTime"],
                "end_time": s["endTime"]
            }
            datas.append(data)
        return datas
