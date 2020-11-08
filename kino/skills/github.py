import arrow
import datetime
from github import Github
from hbconfig import Config

from kino.slack.resource import MsgResource
from kino.slack.slackbot import SlackerAdapter
from kino.slack.plot import Plot

from kino.utils.arrow import ArrowUtil
from kino.utils.data_handler import DataHandler
from kino.utils.score import Score


class GithubManager(object):
    def __init__(self, slackbot=None):
        self.data_handler = DataHandler()

        self.username = Config.open_api.github.USERNAME
        self.github = Github(Config.open_api.github.ACCESS_TOKEN)

        if slackbot is None:
            self.slackbot = SlackerAdapter(
                channel=Config.slack.channel.get("REPORT", "#general")
            )
        else:
            self.slackbot = slackbot

    def commit(self, timely="daily"):
        events = self.github.get_user(self.username).get_events()

        if isinstance(timely, int):
            point_start = self.__time_point(timely)
            point_end = self.__time_point(timely + 1)

            commit_count = self.__get_event_count(events, point_start, point_end)
            return commit_count

        elif timely == "daily":
            point_start = self.__time_point(0)
            point_end = self.__time_point(1)

            commit_count = self.__get_event_count(events, point_start, point_end)
            if commit_count == 0:
                self.slackbot.send_message(text=MsgResource.GITHUB_COMMIT_EMPTY)
            else:
                self.slackbot.send_message(
                    text=MsgResource.GITHUB_COMMIT_EXIST(commit_count=commit_count)
                )

        elif timely == "weekly":
            commit_count_list = []
            for i in range(-6, 1, 1):
                record = self.data_handler.read_record(days=i)
                commit_count_list.append(record.get("Github", 0))

            date = [-6, -5, -4, -3, -2, -1, 0]
            x_ticks = ArrowUtil.format_weekly_date()
            y_ticks = [i for i in range(max(commit_count_list) + 1)]

            f_name = "github_weekly_commit.png"
            title = "Github Commit"

            Plot.make_bar(
                date,
                commit_count_list,
                f_name,
                x_ticks=x_ticks,
                y_ticks=y_ticks,
                x_label="Commit Count",
                title=title,
            )
            self.slackbot.file_upload(
                f_name, title=title, comment=MsgResource.GITHUB_COMMIT_WEEKLY
            )

        elif timely == "ten_days":
            commit_count_list = []
            for i in range(-9, 1, 1):
                point_start = self.__time_point(i)
                point_end = self.__time_point(i + 1)
                commit_count_list.append(
                    self.__get_event_count(events, point_start, point_end)
                )
            return commit_count_list

    def __time_point(self, days):
        today = arrow.now()
        point_date = today.shift(days=days)
        point_date = datetime.datetime(
            point_date.year, point_date.month, point_date.day
        )
        return point_date - datetime.timedelta(hours=9)

    def __get_event_count(self, events, start, end):
        commit_events = []
        for event in events:
            if event.created_at > end:
                continue
            if start < event.created_at < end:
                if event.type in ["PushEvent", "PullRequestEvent"]:
                    commit_events.append(event)
            else:
                break
        return len(commit_events)

    def get_point(self):
        commit_count = sum(self.commit(timely="ten_days"))
        return Score.percent(commit_count, 100, 10)
