import arrow
import datetime

from github import Github

import slack
from slack import MsgResource
import utils


class GithubManager(object):

    def __init__(self):
        self.config = utils.Config()

        self.username = self.config.open_api['github']['USERNAME']
        password = self.config.open_api['github']['PASSWORD']
        self.github = Github(self.username, password)
        self.events = None

        self.slackbot = slack.SlackerAdapter()
        self.plot = slack.Plot

    def commit(self, timely="daily"):
        if timely == "daily":
            point_start = self.__time_point(0)
            point_end = self.__time_point(1)

            commit_count = self.__get_event_count(point_start, point_end)
            if commit_count == 0:
                self.slackbot.send_message(
                    text=MsgResource.GITHUB_COMMIT_EMPTY)
            else:
                self.slackbot.send_message(
                    text=MsgResource.GITHUB_COMMIT_EXIST + str(commit_count))

        elif timely == "weekly":
            commit_count_list = []
            for i in range(-6, 1, 1):
                point_start = self.__time_point(i)
                point_end = self.__time_point(i + 1)
                commit_count_list.append(
                    self.__get_event_count(
                        point_start, point_end))

            date = [-6, -5, -4, -3, -2, -1, 0]
            x_ticks = [
                '6 day before',
                '5 day before',
                '4 day before',
                '3 day before',
                '2 day before',
                'yesterday',
                'today']
            y_ticks = [i for i in range(max(commit_count_list) + 1)]

            f_name = "github_weekly_commit.png"
            title = "Github Commit"

            self.plot.make_bar(
                date,
                commit_count_list,
                f_name,
                x_ticks=x_ticks,
                y_ticks=y_ticks,
                x_label="Commit Count",
                title=title)
            self.slackbot.file_upload(
                f_name, title=title, comment=MsgResource.GITHUB_COMMIT_WEEKLY)

        elif timely == "ten_days":
            commit_count_list = []
            for i in range(-9, 1, 1):
                point_start = self.__time_point(i)
                point_end = self.__time_point(i + 1)
                commit_count_list.append(
                    self.__get_event_count(
                        point_start, point_end))
            return commit_count_list

    def __time_point(self, days):
        today = arrow.now()
        point_date = today.replace(days=days)
        point_date = datetime.datetime(
            point_date.year, point_date.month, point_date.day)
        return point_date - datetime.timedelta(hours=9)

    def __get_event_count(self, start, end):
        if self.events is None:
            self.events = self.github.get_user(self.username).get_events()
        commit_events = []
        for event in self.events:
            if event.created_at > end:
                continue
            if start < event.created_at < end:
                if event.type in ['PushEvent', 'PullRequestEvent']:
                    commit_events.append(event)
            else:
                break
        return len(commit_events)

    def get_point(self):
        commit_count = sum(self.commit(timely="ten_days"))
        return utils.Score().percent(commit_count, 100, 10)
