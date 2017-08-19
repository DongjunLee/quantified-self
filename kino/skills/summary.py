
import arrow

from .rescue_time import RescueTime
from .toggl import TogglManager
from .todoist import TodoistManager
from .github import GithubManager

from ..slack.resource import MsgResource
from ..slack.slackbot import SlackerAdapter
from ..slack.template import MsgTemplate
from ..slack.plot import Plot

from ..utils.arrow import ArrowUtil
from ..utils.config import Config
from ..utils.data_handler import DataHandler
from ..utils.profile import Profile
from ..utils.score import Score
from ..utils.state import State


class Summary(object):

    def __init__(self, slackbot=None):
        self.config = Config()
        self.data_handler = DataHandler()
        self.column_list = [
            "Attention",
            "Productive",
            "Happy",
            "Sleep",
            "REPEAT_TASK",
            "Total"]

        if self.config.profile["personal"]:
            from ..utils.profile import Profile
            self.profile = Profile()

        if slackbot is None:
            self.slackbot = SlackerAdapter(
                channel=self.config.channel['REPORT'])
        else:
            self.slackbot = slackbot

    def total_score(self):
        today_data = self.__get_total_score()
        self.data_handler.edit_record(today_data)

        color = MsgResource.SCORE_COLOR(today_data['Total'])
        today_data['Color'] = color

        yesterday_data = self.__get_total_score(-1)
        for k, v in today_data.items():
            if isinstance(v, float):
                y_point = yesterday_data.get(k, False)
                if not y_point:
                    continue
                else:
                    diff = v - float(y_point)
                    diff = round(diff * 100) / 100

                if diff > 0:
                    diff = "+" + str(diff)
                else:
                    diff = str(diff)
                today_data[k] = str(v) + " (" + diff + ")"
            elif isinstance(v, bool):
                if v:
                    today_data[k] = "O"
                else:
                    today_data[k] = "X"

        record = self.data_handler.read_record()
        activity = record.get('activity', {})

        # Sleep Time
        go_to_bed = activity.get('go_to_bed', None)
        wake_up = activity.get('wake_up', None)

        if (go_to_bed is not None and wake_up is not None):
            go_to_bed_time = arrow.get(go_to_bed)
            wake_up_time = arrow.get(wake_up)

            sleep_hour = ArrowUtil.get_curr_time_diff(
                start=go_to_bed_time, stop=wake_up_time, base_hour=True)
            today_data['Sleep'] = go_to_bed_time.format("HH:mm") + " ~ " + wake_up_time.format(
                "HH:mm") + " : " + str(sleep_hour) + "h (" + str(today_data['Sleep']) + ")"

        # Working Hour
        in_company = activity.get('in_company', None)
        out_company = activity.get('out_company', None)

        if (in_company is not None and out_company is not None):
            in_company_time = arrow.get(in_company)
            out_company_time = arrow.get(out_company)

            working_hour = ArrowUtil.get_curr_time_diff(
                start=in_company_time, stop=out_company_time, base_hour=True)
            today_data['Working Hour'] = in_company_time.format(
                "HH:mm") + " ~ " + out_company_time.format("HH:mm") + " : " + str(working_hour) + "h"

        attachments = MsgTemplate.make_summary_template(today_data)
        self.slackbot.send_message(attachments=attachments)

    def __get_total_score(self, days="today"):
        if days == "today":
            attention = self.__attention_score()
            productive = self.__productive_score()
            happy = self.__happy_score()
            sleep = self.__sleep_score()
            repeat = self.__repeat_task_score()

            today_data = self.data_handler.read_record()
            diary = today_data.get('Diary', False)
            exercise = today_data.get('Exercise', False)
            bat = today_data.get('BAT', False)

            total = (
                Score.percent(
                    attention,
                    self.profile.get_score('ATTENTION'),
                    100) +
                Score.percent(
                    happy,
                    self.profile.get_score('HAPPY'),
                    100) +
                Score.percent(
                    productive,
                    self.profile.get_score('PRODUCTIVE'),
                    100) +
                Score.percent(
                    sleep,
                    self.profile.get_score('SLEEP'),
                    100) +
                Score.percent(
                    repeat,
                    self.profile.get_score('REPEAT_TASK'),
                    100))

            if diary:
                total += self.profile.get_score('DIARY')
            if exercise:
                total += self.profile.get_score('EXERCISE')
            if bat:
                total += self.profile.get_score('BAT')

            if total > 100:
                total = 100

            data = {
                "Attention": round(attention * 100) / 100,
                "Happy": round(happy * 100) / 100,
                "Productive": round(productive * 100) / 100,
                "Sleep": round(sleep * 100) / 100,
                "REPEAT_TASK": round(repeat * 100) / 100,
                "Diary": diary,
                "Exercise": exercise,
                "BAT": bat,
                "Total": round(total * 100) / 100
            }
            return data
        elif isinstance(days, int):
            data = self.data_handler.read_record(days=days)
            for c in self.column_list:
                if c not in data:
                    data[c] = 0
            return data

    def __productive_score(self):
        rescue_time_point = RescueTime().get_point()
        toggl_point = TogglManager().get_point()
        github_point = GithubManager().get_point()
        todoist_point = TodoistManager().get_point()

        data = {
            "rescue_time": round(rescue_time_point * 100) / 100,
            "toggl": round(toggl_point * 100) / 100,
            "github": round(github_point * 100) / 100,
            "todoist": round(todoist_point * 100) / 100
        }
        self.data_handler.edit_record(('productive', data))

        base_point = 0
        rescue_time_ratio = self.profile.get_score('productives')[
            'RESCUE_TIME']
        github_ratio = self.profile.get_score('productives')['GITHUB']
        todoist_ratio = self.profile.get_score('productives')['TODOIST']
        toggl_ratio = self.profile.get_score('productives')['TOGGL']

        if self.is_holiday():
            base_point = self.profile.get_score('HOLIDAY_BASE')
            holiday_ratio = self.profile.get_score('HOLIDAY_RATIO')

            rescue_time_ratio *= holiday_ratio
            github_ratio *= holiday_ratio
            todoist_ratio *= holiday_ratio
            toggl_ratio *= holiday_ratio

        rescue_time_point = Score.percent(
            rescue_time_point, rescue_time_ratio, 100)
        github_point = Score.percent(github_point, github_ratio, 100)
        todoist_point = Score.percent(todoist_point, todoist_ratio, 100)
        toggl_point = Score.percent(toggl_point, toggl_ratio, 100)
        return (
            base_point +
            rescue_time_point +
            github_point +
            todoist_point +
            toggl_point)

    def __attention_score(self):
        attention_data = self.data_handler.read_record().get('attention', {})
        if len(attention_data) > 0:
            return sum(list(map(lambda x: int(x),
                                attention_data.values()))) / len(attention_data)
        else:
            return 80

    def __happy_score(self):
        happy_data = self.data_handler.read_record().get('happy', {})
        if len(happy_data) > 0:
            return sum(
                list(map(lambda x: int(x), happy_data.values()))) / len(happy_data)
        else:
            return 80

    def __sleep_score(self):
        activity_data = self.data_handler.read_record().get('activity', {})

        go_to_bed_time = arrow.get(activity_data.get('go_to_bed', None))
        wake_up_time = arrow.get(activity_data.get('wake_up', None))

        sleep_time = (wake_up_time - go_to_bed_time).seconds / 60 / 60
        sleep_time = sleep_time * 100

        if sleep_time > 800:
            sleep_time -= (sleep_time - 800)

        if sleep_time > 700:
            sleep_time = 700

        return Score.percent(sleep_time, 100, 700)

    def __repeat_task_score(self):
        todoist = TodoistManager()
        minus_point = 15
        if self.is_holiday():
            minus_point /= 2
        return 100 - (minus_point * todoist.get_repeat_task_count())

    def record_write_diary(self):
        self.data_handler.edit_record(('Diary', True))

    def record_exercise(self):
        self.data_handler.edit_record(('Exercise', True))

    def record_bat(self):
        self.data_handler.edit_record(('BAT', True))

    def record_holiday(self, dnd):
        self.data_handler.edit_record(('Holiday', dnd))

    def is_holiday(self):
        record = self.data_handler.read_record()
        holiday = record.get('Holiday', None)
        if holiday is None:
            return not ArrowUtil.is_weekday()
        else:
            return holiday

    def check_go_to_bed(self):
        state = State()
        state.check()
        presence_log = state.current[state.SLEEP]
        if presence_log['presence'] == 'away':
            go_to_bed_time = arrow.get(presence_log['time'])
            self.data_handler.edit_record_with_category(
                'activity', ('go_to_bed', str(go_to_bed_time)))

    def check_commit_count(self):
        github = GithubManager()
        commit_count = github.commit(timely=-1)
        self.data_handler.edit_record(('Github', commit_count))

    def total_chart(self):
        records = []
        for i in range(-6, 1, 1):
            records.append(self.__get_total_score(i))

        date = [-6, -5, -4, -3, -2, -1, 0]
        x_ticks = ArrowUtil.format_weekly_date()

        legend = self.column_list
        data = []
        for l in legend:
            data.append(list(map(lambda x: x[l], records)))

        f_name = "total_weekly_report.png"
        title = "Total Report"

        Plot.make_line(date, data, f_name, legend=legend, x_ticks=x_ticks,
                       x_label="Total Point", y_label="Days", title=title)
        self.slackbot.file_upload(
            f_name, title=title, comment=MsgResource.TOTAL_REPORT)
