
import arrow
import collections
import re

import nlp
import slack
from slack import MsgResource
import utils

class Happy(object):

    def __init__(self, text=None):
        self.input = text
        self.slackbot = slack.SlackerAdapter()
        self.data_handler = utils.DataHandler()
        self.fname = "happy/" + arrow.now().format('YYYY-MM-DD') + ".json"
        self.plot = slack.Plot

    def question(self, step=0, params=None):
        state = nlp.State()

        def step_0(params):
            self.slackbot.send_message(text=MsgResource.HAPPY_QUESTION_STEP_0)
            state.start("skills/Happy", "question")

        def step_1(params):
            if params is None:
                return

            numbers = re.findall(r'\d+', params)
            if len(numbers) != 1:
                self.slackbot.send_message(text=MsgResource.NOT_UNDERSTANDING)
                return

            now = arrow.now()
            time = now.format('HH:mm')

            happy_point = numbers[0]
            happy_data = self.data_handler.read_file(self.fname)
            happy_data[time] = happy_point
            self.data_handler.write_file(self.fname, happy_data)

            self.slackbot.send_message(text=MsgResource.HAPPY_QUESTION_STEP_1(happy_point))
            state.complete()

        locals()["step_" + str(step)](params)

    def report(self, timely="daily"):
        if timely == "daily":
            happy_data = self.get_data()

            def convert_time(time):
                hour, minute = time[0].split(":")
                total_minute = int(hour) * 60 + int(minute)
                return total_minute

            ordered_happy_data = collections.OrderedDict(sorted(happy_data.items(), key=convert_time))

            x_ticks = list(ordered_happy_data.keys()) # time
            time = list(range(len(x_ticks)))
            happy_point_list = list(ordered_happy_data.values()) # happy_point

            f_name = "happy_daily_report.png"
            title = "Happy Report"

            self.plot.make_line(time, happy_point_list, f_name, x_ticks=x_ticks,
                                x_label="Happy Point", y_label="Time", title=title)
            self.slackbot.file_upload(f_name, title=title, comment=MsgResource.HAPPY_REPORT)

    def get_data(self):
        return self.data_handler.read_file(self.fname)
