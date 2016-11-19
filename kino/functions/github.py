import datetime

from github import Github

import slack
from slack import MsgResource
import utils

class GithubManager(object):

    def __init__(self):
        self.config = utils.Config().github
        self.username = self.config["USERNAME"]
        password = self.config["PASSWORD"]
        self.github = Github(self.username, password)
        self.slackbot = slack.SlackerAdapter()

    def daily_commit_check(self):
        today = datetime.datetime.today()
        today_date = datetime.datetime(today.year, today.month, today.day)
        today_date_ko = today_date - datetime.timedelta(hours=9)

        commit_events = []
        for event in self.github.get_user(self.username).get_events():
            if event.created_at > today_date_ko:
                if event.type in ['PushEvent', 'PullRequestEvent']:
                    commit_events.append(event)
            else:
                break
        if len(commit_events) == 0:
            self.slackbot.send_message(text=MsgResource.GITHUB_COMMIT_EMPTY)
        else:
            self.slackbot.send_message(text=MsgResource.GITHUB_COMMIT_EXIST + str(len(commit_events)))
