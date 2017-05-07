
import arrow
import collections
import re

from ..dialog.dialog_manager import DialogManager

from ..slack.resource import MsgResource
from ..slack.slackbot import SlackerAdapter
from ..slack.plot import Plot

from ..utils.data_handler import DataHandler
from ..utils.score import Score
from ..utils.state import State


class Happy(object):

    def __init__(self, text=None):
        self.input = text
        self.slackbot = SlackerAdapter()
        self.data_handler = DataHandler()

    def question(self, step=0, params=None):
        state = State()

        def step_0(params):
            flow = DialogManager().get_flow(is_raw=True)
            if flow.get('class', None) == "Happy":
                pass
            else:
                self.slackbot.send_message(
                    text=MsgResource.HAPPY_QUESTION_STEP_0)
                state.flow_start("Happy", "question")

        def step_1(params):
            if params is None:
                return

            numbers = re.findall(r'\d+', params)
            if len(numbers) != 1:
                self.slackbot.send_message(text=MsgResource.FLOW_HAPPY)
                return

            now = arrow.now()
            time = now.format('HH:mm')
            happy_point = numbers[0]
            self.data_handler.edit_record_with_category(
                'happy', (time, happy_point))

            self.slackbot.send_message(
                text=MsgResource.HAPPY_QUESTION_STEP_1(happy_point))
            state.flow_complete()

        locals()["step_" + str(step)](params)

    def report(self, timely="daily"):
        if timely == "daily":
            happy_data = self.data_handler.read_record().get('happy', {})

            def convert_time(time):
                hour, minute = time[0].split(":")
                total_minute = int(hour) * 60 + int(minute)
                return total_minute

            ordered_happy_data = collections.OrderedDict(
                sorted(happy_data.items(), key=convert_time))

            x_ticks = list(ordered_happy_data.keys())  # time
            time = list(range(len(x_ticks)))
            happy_point_list = list(ordered_happy_data.values())  # happy_point

            f_name = "happy_daily_report.png"
            title = "Happy Report"

            Plot.make_line(
                time,
                happy_point_list,
                f_name,
                x_ticks=x_ticks,
                x_label="Happy Point",
                y_label="Time",
                title=title)
            self.slackbot.file_upload(
                f_name, title=title, comment=MsgResource.HAPPY_REPORT)


class Attention(object):

    def __init__(self, text=None):
        self.input = text
        self.slackbot = SlackerAdapter()
        self.data_handler = DataHandler()

    def question(self, step=0, params=None):
        state = State()

        def step_0(params):
            flow = DialogManager().get_flow(is_raw=True)
            if flow.get('class', None) == "Attention":
                pass
            else:
                self.slackbot.send_message(
                    text=MsgResource.ATTENTION_QUESTION_STEP_0)
                state.flow_start("Attention", "question")

        def step_1(params):
            if params is None:
                return

            numbers = re.findall(r'\d+', params)
            if len(numbers) != 1:
                self.slackbot.send_message(text=MsgResource.FLOW_ATTENTION)
                return

            now = arrow.now()
            time = now.format('HH:mm')
            attention_point = numbers[0]
            self.data_handler.edit_record_with_category(
                'attention', (time, attention_point))

            self.slackbot.send_message(
                text=MsgResource.ATTENTION_QUESTION_STEP_1(attention_point))
            state.flow_complete()

        locals()["step_" + str(step)](params)

    def report(self, timely="daily"):
        if timely == "daily":
            attention_data = self.data_handler.read_record().get('attention', {})

            def convert_time(time):
                hour, minute = time[0].split(":")
                total_minute = int(hour) * 60 + int(minute)
                return total_minute

            ordered_attention_data = collections.OrderedDict(
                sorted(attention_data.items(), key=convert_time))

            x_ticks = list(ordered_attention_data.keys())  # time
            time = list(range(len(x_ticks)))
            attention_point_list = list(ordered_attention_data.values())  # attention_point

            f_name = "attention_daily_report.png"
            title = "attention Report"

            Plot.make_line(
                time,
                attention_point_list,
                f_name,
                x_ticks=x_ticks,
                x_label="attention Point",
                y_label="Time",
                title=title)
            self.slackbot.file_upload(
                f_name, title=title, comment=MsgResource.ATTENTION_REPORT)


