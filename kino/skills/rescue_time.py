import matplotlib
matplotlib.use('TkAgg')

import arrow
import itertools
import requests
from hbconfig import Config

from ..slack.resource import MsgResource
from ..slack.slackbot import SlackerAdapter
from ..slack.plot import Plot

from ..utils.score import Score


class RescueTime(object):

    def __init__(self, slackbot=None):

        if slackbot is None:
            self.slackbot = SlackerAdapter(
                channel=Config.slack.channel.get('REPORT', "#general"))
        else:
            self.slackbot = slackbot

    def efficiency(self, timely="daily"):
        now = arrow.now()
        if timely == "daily":
            before_days = now.replace(days=0)
        elif timely == "weekly":
            before_days = now.replace(days=-6)

        start = now.format('YYYY-MM-DD')
        end = before_days.format('YYYY-MM-DD')

        response = self.__data_request(start, end).json()
        total_data = list(map(lambda x: (x[0][11:16], x[4]), response['rows']))
        avg_data = self.__get_avg_data(total_data)

        f_name = "rescuetime_efficiency.png"
        title = 'Data from ' + start + ' to ' + end

        Plot.make_efficiency_date(
            total_data,
            avg_data,
            f_name,
            x_label="Efficiency",
            y_label="Hours",
            title=title)
        self.slackbot.file_upload(
            f_name,
            title=title,
            comment=MsgResource.RESCUETIME_EFFICIENCY)

    def __data_request(self, start, end):
        url = "https://www.rescuetime.com/anapi/data/?"
        params = {
            "pv": "interval",
            "rk": "efficiency",
            "format": "json",
            "rs": "hour",
            "rb": start,
            "re": end,
            "rtapi_key": Config.open_api.rescue_time.TOKEN
        }

        for k, v in params.items():
            url += "&" + k + "=" + v
        return requests.get(url)

    def __get_avg_data(self, total_data):
        avg_data = []
        for time, row in itertools.groupby(total_data, lambda x: x[0]):
            biaslist = [float(x[1]) for x in row]
            biasavg = round(float(sum(biaslist)) / len(biaslist), 1)
            avg_data.append((time, biasavg))
        return avg_data

    def get_point(self):
        response = self.__data_summary_request().json()
        today = response[0]
        return Score.percent(today['productivity_pulse'], 100, 80)

    def __data_summary_request(self):
        url = "https://www.rescuetime.com/anapi/daily_summary_feed?"
        return requests.get(
            url +
            "key=" +
            Config.open_api.rescue_time.TOKEN)
