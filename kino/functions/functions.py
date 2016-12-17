# -*- coding: utf-8 -*-

import functions
import slack
import utils

class Functions(object):

    def __init__(self):
        self.data_handler = utils.DataHandler()
        self.slackbot = slack.SlackerAdapter()
        self.registered = RegisteredFuctions().list

    def send_message(self, text=None):
        self.slackbot.send_message(text=text)

    def forecast(self, timely="current"):
        weather = functions.Weather()
        weather.read(timely=timely)

    def github_commit(self, timely="daily"):
        github = functions.GithubManager()
        github.commit(timely)

    def happy(self, text="busy"):
        happy = functions.Happy(text=text)
        happy.question()

    def happy_report(self, timely="daily"):
        happy = functions.Happy()
        happy.report(timely=timely)

    def today_briefing(self):
        todoist = functions.TodoistManager()
        todoist.today_briefing()

    def today_summary(self):
        todoist = functions.TodoistManager()
        todoist.today_summary()

    def toggl_timer(self, description=None):
        toggl = functions.TogglManager()
        toggl.timer(description=description)

    def toggl_checker(self):
        toggl = functions.TogglManager()
        toggl.check_toggl_timer()

    def toggl_report(self, kind="chart", timely="weekly"):
        toggl = functions.TogglManager()
        toggl.report(kind=kind, timely=timely)

    def maxim_nietzsche(self):
        maxim = functions.Maxim()
        maxim.nietzsche()

class RegisteredFuctions(object):
    class __List:
        def __init__(self):
            self.list = utils.DataHandler().read_file("functions.json")

    instance = None
    def __init__(self):
        if not RegisteredFuctions.instance:
            RegisteredFuctions.instance = RegisteredFuctions.__List()

    def __getattr__(self, name):
        return getattr(self.instance, name)
