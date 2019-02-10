
import arrow
from hbconfig import Config

from kino.skills.fitbit import Fitbit
from kino.skills.github import GithubManager
from kino.skills.toggl import TogglManager
from kino.skills.todoist import TodoistManager
from kino.skills.trello import TrelloManager
from kino.skills.rescue_time import RescueTime

from kino.slack.resource import MsgResource
from kino.slack.slackbot import SlackerAdapter
from kino.slack.template import MsgTemplate
from kino.slack.plot import Plot

from kino.utils.arrow import ArrowUtil
from kino.utils.data_handler import DataHandler
from kino.utils.score import Score


class Summary(object):
    def __init__(self, slackbot=None):
        self.data_handler = DataHandler()
        self.column_list = [
            "attention",
            "productive",
            "happy",
            "sleep",
            "repeat_task",
            "total",
        ]

        if Config.profile.personal:
            from ..utils.profile import Profile

            self.profile = Profile()

        if slackbot is None:
            self.slackbot = SlackerAdapter(
                channel=Config.slack.channel.get("REPORT", "#general")
            )
        else:
            self.slackbot = slackbot

    def total_score(self):
        today_data = self.__get_total_score()
        self.data_handler.edit_summary(today_data)

        color = MsgResource.SCORE_COLOR(today_data["total"])
        today_data["Color"] = color

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
        activity = record.get("activity", {})

        # Sleep Time
        go_to_bed = activity.get("go_to_bed", None)
        wake_up = activity.get("wake_up", None)

        if go_to_bed is not None and wake_up is not None:
            go_to_bed_time = arrow.get(go_to_bed)
            wake_up_time = arrow.get(wake_up)

            sleep_hour = ArrowUtil.get_curr_time_diff(
                start=go_to_bed_time, stop=wake_up_time, base_hour=True
            )
            today_data["Sleep"] = (
                go_to_bed_time.format("HH:mm")
                + " ~ "
                + wake_up_time.format("HH:mm")
                + " : "
                + str(sleep_hour)
                + "h ("
                + str(today_data["Sleep"])
                + ")"
            )

        # Working Hour
        in_company = activity.get("in_company", None)
        out_company = activity.get("out_company", None)

        if in_company is not None and out_company is not None:
            in_company_time = arrow.get(in_company)
            out_company_time = arrow.get(out_company)

            working_hour = ArrowUtil.get_curr_time_diff(
                start=in_company_time, stop=out_company_time, base_hour=True
            )
            today_data["Working Hour"] = (
                in_company_time.format("HH:mm")
                + " ~ "
                + out_company_time.format("HH:mm")
                + " : "
                + str(working_hour)
                + "h"
            )

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
            diary = today_data.get("Diary", False)
            exercise = today_data.get("Exercise", False)
            bat = today_data.get("BAT", False)

            total = (
                Score.percent(attention, Config.score.get("ATTENTION", 20), 100)
                + Score.percent(happy, Config.score.get("HAPPY", 10), 100)
                + Score.percent(productive, Config.score.get("PRODUCTIVE", 30), 100)
                + Score.percent(sleep, Config.score.get("SLEEP", 20), 100)
                + Score.percent(repeat, Config.score.get("REPEAT_TASK", 10), 100)
            )

            if diary:
                total += Config.score.get("DIARY", 5)
            if exercise:
                total += Config.score.get("EXERCISE", 5)
            if bat:
                total += Config.score.get("BAT", 5)

            if total > 100:
                total = 100

            data = {
                "attention": round(attention * 100) / 100,
                "happy": round(happy * 100) / 100,
                "productive": round(productive * 100) / 100,
                "sleep": round(sleep * 100) / 100,
                "repeat_task": round(repeat * 100) / 100,
                "do_diary": diary,
                "exercise": exercise,
                "bat": bat,
                "total": round(total * 100) / 100,
            }
            return data
        elif isinstance(days, int):
            data = self.data_handler.read_summary(days=days)
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
            "productive_details": {
                "rescue_time": round(rescue_time_point * 100) / 100,
                "toggl": round(toggl_point * 100) / 100,
                "github": round(github_point * 100) / 100,
                "todoist": round(todoist_point * 100) / 100,
            }
        }
        self.data_handler.edit_summary(data)

        base_point = 0
        rescue_time_ratio = Config.score.productives.get("RESCUE_TIME", 10)
        github_ratio = Config.score.productives.get("GITHUB", 10)
        todoist_ratio = Config.score.productives.get("TODOIST", 50)
        toggl_ratio = Config.score.productives.get("TOGGL", 30)

        if self.is_holiday():
            base_point = Config.score.get("HOLIDAY_BASE", 50)
            holiday_ratio = Config.score.get("HOLIDAY_RATIO", 0.5)

            rescue_time_ratio *= holiday_ratio
            github_ratio *= holiday_ratio
            todoist_ratio *= holiday_ratio
            toggl_ratio *= holiday_ratio

        rescue_time_point = Score.percent(rescue_time_point, rescue_time_ratio, 100)
        github_point = Score.percent(github_point, github_ratio, 100)
        todoist_point = Score.percent(todoist_point, todoist_ratio, 100)
        toggl_point = Score.percent(toggl_point, toggl_ratio, 100)
        return (
            base_point + rescue_time_point + github_point + todoist_point + toggl_point
        )

    def __attention_score(self):
        DEFAULT_SCORE = 60
        SCORE_UNIT = 20

        attention_data = self.data_handler.read_record().get("attention", {})
        if len(attention_data) > 0:
            return sum(list(map(lambda x: int(x * SCORE_UNIT), attention_data.values()))) / len(
                attention_data
            )
        else:
            return DEFAULT_SCORE

    def __happy_score(self):
        DEFAULT_SCORE = 60
        SCORE_UNIT = 20

        happy_data = self.data_handler.read_record().get("happy", {})
        if len(happy_data) > 0:
            return sum(list(map(lambda x: int(x * SCORE_UNIT), happy_data.values()))) / len(
                happy_data
            )
        else:
            return DEFAULT_SCORE

    def __sleep_score(self):
        self.__get_sleep_time_with_fitbit()

        activity_data = self.data_handler.read_record().get("activity", {})
        sleep_data = activity_data.get("sleep", [])

        if len(sleep_data) == 0:
            sleep_start_time = arrow.now()
            sleep_end_time = arrow.now()
        else:
            for s in sleep_data:
                if s["is_main"]:
                    sleep_start_time = arrow.get(s.get("start_time", None))
                    sleep_end_time = arrow.get(s.get("end_time", None))

        sleep_time = (sleep_end_time - sleep_start_time).seconds / 60 / 60
        sleep_time = sleep_time * 100

        if sleep_time > 800:
            sleep_time -= sleep_time - 800

        if sleep_time > 700:
            sleep_time = 700

        return Score.percent(sleep_time, 100, 700)

    def __get_sleep_time_with_fitbit(self):
        fitbit = Fitbit()
        sleep_data = fitbit.get_sleeps()
        self.data_handler.edit_activity("sleep", sleep_data)

    def __repeat_task_score(self):
        trello = TrelloManager()
        minus_point = 15
        if self.is_holiday():
            minus_point /= 2
        return 100 - (minus_point * trello.get_card_count_by_list_name("Tasks"))

    def record_write_diary(self):
        self.data_handler.edit_summary({"do_diary", True})

    def record_exercise(self):
        self.data_handler.edit_summary({"do_exercise", True})

    def record_bat(self):
        self.data_handler.edit_summary({"bat", True})

    def record_holiday(self, dnd):
        self.data_handler.edit_summary({"is_holiday", dnd})

    def is_holiday(self):
        record = self.data_handler.read_record()
        holiday = record.get("Holiday", None)
        if holiday is None:
            return not ArrowUtil.is_weekday()
        else:
            return holiday

    def check_sleep_time(self):
        self.slackbot.send_message(text=MsgResource.GOOD_MORNING)

        record = self.data_handler.read_record()
        activity = record.get("activity", {})
        go_to_bed_time = arrow.get(activity.get("go_to_bed", None))

        wake_up_time = arrow.now()
        self.data_handler.edit_record_with_category(
            "activity", ("wake_up", str(wake_up_time))
        )

        sleep_time = (wake_up_time - go_to_bed_time).seconds / 60 / 60
        sleep_time = round(sleep_time * 100) / 100

        self.data_handler.edit_record(("Sleep", str(sleep_time)))

        self.slackbot.send_message(
            text=MsgResource.SLEEP_TIME(
                bed_time=go_to_bed_time.format("HH:mm"),
                wakeup_time=wake_up_time.format("HH:mm"),
                diff_h=str(sleep_time),
            )
        )

    def check_go_to_bed(self):
        go_to_bed_time = arrow.now()
        self.data_handler.edit_record_with_category(
            "activity", ("go_to_bed", str(go_to_bed_time))
        )

        self.slackbot.send_message(text=MsgResource.GOOD_NIGHT)

        # slack presence issue
        # state = State()
        # state.check()
        # presence_log = state.current[state.SLEEP]
        # if presence_log['presence'] == 'away':
        # go_to_bed_time = arrow.get(presence_log['time'])
        # self.data_handler.edit_record_with_category(
        # 'activity', ('go_to_bed', str(go_to_bed_time)))

    def check_commit_count(self):
        github = GithubManager()
        commit_count = github.commit(timely=-1)
        self.data_handler.edit_summary(("github_commit_count", commit_count))

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

        Plot.make_line(
            date,
            data,
            f_name,
            legend=legend,
            x_ticks=x_ticks,
            x_label="Total Point",
            y_label="Days",
            title=title,
        )
        self.slackbot.file_upload(f_name, title=title, comment=MsgResource.TOTAL_REPORT)
