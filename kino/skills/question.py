
import arrow
import collections
import re

from ..dialog.dialog_manager import DialogManager

from ..slack.resource import MsgResource
from ..slack.slackbot import SlackerAdapter
from ..slack.plot import Plot

from ..utils.config import Config
from ..utils.data_handler import DataHandler
from ..utils.state import State


class Question(object):

    def __init__(self):
        self.category = ""
        self.msg_question_step_0 = ""
        self.msg_question_step_1 = ""
        self.msg_flow = ""
        self.msg_report = ""
        self.slackbot = SlackerAdapter()

    @property
    def config(self):
        return Config()

    @property
    def data_handler(self):
        return DataHandler()

    def question(self, step=0, params=None):
        state = State()

        def step_0(params):
            flow = DialogManager().get_flow(is_raw=True)
            if flow.get('class', None) == self.__class__.__name__:
                pass
            else:
                self.slackbot.send_message(
                    text=self.msg_question_step_0)
                state.flow_start(self.__class__.__name__, "question")

        def step_1(params):
            if params is None:
                return

            numbers = re.findall(r'\d+', params)
            if len(numbers) != 1:
                self.slackbot.send_message(text=self.msg_flow)
                return

            if numbers > 100:
                numbers = 100

            now = arrow.now()
            time = now.format('HH:mm')
            point = numbers[0]
            self.data_handler.edit_record_with_category(
                self.category, (time, point))

            self.slackbot.send_message(
                text=self.msg_question_step_1(point))
            state.flow_complete()

        locals()["step_" + str(step)](params)

    def report(self, timely="daily"):

        if timely == "daily":
            question_data = self.data_handler.read_record().get(self.category, {})

            def convert_time(time):
                hour, minute = time[0].split(":")
                total_minute = int(hour) * 60 + int(minute)
                return total_minute

            ordered_question_data = collections.OrderedDict(
                sorted(question_data.items(), key=convert_time))

            x_ticks = list(ordered_question_data.keys())  # time
            time = list(range(len(x_ticks)))
            point_list = list(ordered_question_data.values())  # question_point

            f_name = self.category + "_daily_report.png"
            title = self.category + " Report"

            Plot.make_line(
                time,
                point_list,
                f_name,
                x_ticks=x_ticks,
                x_label=self.category + " Point",
                y_label="Time",
                title=title)
            self.slackbot.file_upload(
                f_name,
                title=title,
                channel=self.config.channel['REPORT'],
                comment=self.msg_report)


class HappyQuestion(Question):

    def __init__(self, slackbot=None):
        self.category = "happy"
        self.msg_question_step_0 = MsgResource.HAPPY_QUESTION_STEP_0
        self.msg_question_step_1 = MsgResource.HAPPY_QUESTION_STEP_1
        self.msg_flow = MsgResource.FLOW_HAPPY
        self.msg_report = MsgResource.HAPPY_REPORT

        if slackbot is None:
            self.slackbot = SlackerAdapter(
                channel=self.config.channel["DEFAULT"])
        else:
            self.slackbot = slackbot


class AttentionQuestion(Question):

    def __init__(self, slackbot=None):
        self.category = "attention"
        self.msg_question_step_0 = MsgResource.ATTENTION_QUESTION_STEP_0
        self.msg_question_step_1 = MsgResource.ATTENTION_QUESTION_STEP_1
        self.msg_flow = MsgResource.FLOW_ATTENTION
        self.msg_report = MsgResource.ATTENTION_REPORT

        if slackbot is None:
            self.slackbot = SlackerAdapter(channel=self.config.channel["TASK"])
        else:
            self.slackbot = slackbot
