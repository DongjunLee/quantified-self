import matplotlib
matplotlib.use('TkAgg')

import arrow
import itertools
import requests

import slack
from slack import MsgResource
import utils
from utils import Score


class RescueTime(object):

    def __init__(self):
        self.config = utils.Config()
        self.slackbot = slack.SlackerAdapter()
        self.plot = slack.Plot

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

        self.plot.make_efficiency_date(
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
            "rtapi_key": self.config.open_api['rescue_time']['TOKEN']
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
            self.config.open_api['rescue_time']['TOKEN'])
