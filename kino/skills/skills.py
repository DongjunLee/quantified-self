# -*- coding: utf-8 -*-

import skills
import slack
from slack import MsgResource
import utils

class Functions(object):

    def __init__(self):
        self.data_handler = utils.DataHandler()
        self.slackbot = slack.SlackerAdapter()
        self.registered = RegisteredFuctions().list

    def check_go_to_bed(self):
        summary = skills.Summary()
        summary.check_go_to_bed()

    def send_message(self, text=None):
        self.slackbot.send_message(text=text)

    def bus_stop(self, station_id=None, real_time=None):
        if real_time is None:
            real_time = False
        bus = skills.Bus()
        bus.arrive_info(station_id, real_time=real_time)

    def forecast(self, timely="current"):
        if timely is None:
            timely = 'current'
        weather = skills.Weather()
        weather.forecast(timely=timely)

    def air_quality(self):
        weather = skills.Weather()
        weather.air_quality()

    def github_commit(self, timely="daily"):
        if timely is None:
            timely = 'daily'
        github = skills.GithubManager()
        github.commit(timely=timely)

    def happy(self, text="busy"):
        happy = skills.Happy(text=text)
        happy.question()

    def happy_report(self, timely="daily"):
        if timely is None:
            timely = 'daily'
        happy = skills.Happy()
        happy.report(timely=timely)

    def total_score(self):
        summary = skills.Summary()
        summary.total_score()

    def total_chart(self):
        summary = skills.Summary()
        summary.total_chart()

    def translate(self, english="", source="en", target="ko"):
        if source is None:
            source = "en"
        if target is None:
            target = "ko"
        naver = skills.Naver()
        naver.translate(english, source=source, target=target)

    def rescuetime_efficiency(self, timely="daily"):
        if timely is None:
            timely = 'daily'
        rescuetime = skills.RescueTime()
        rescuetime.efficiency(timely=timely)

    def today_briefing(self):
        todoist = skills.TodoistManager()
        todoist.schedule()

    def today_summary(self):
        self.slackbot.send_message(text=MsgResource.TODAY_SUMMARY)

        todoist = skills.TodoistManager()
        todoist.feedback()

        toggl = skills.TogglManager()
        toggl.report(kind="chart", timely="daily")

        rescuetime = skills.RescueTime()
        rescuetime.efficiency(timely="daily")

        happy = skills.Happy()
        happy.report(timely="daily")

        github = skills.GithubManager()
        github.commit(timely="daily")

    def todoist_auto_update(self):
        todoist = skills.TodoistManager()
        todoist.auto_update_tasks()

    def todoist_feedback(self):
        todoist = skills.TodoistManager()
        todoist.feedback()

    def todoist_remain(self):
        todoist = skills.TodoistManager()
        todoist.remain_task()

    def toggl_timer(self, description=None):
        toggl = skills.TogglManager()
        toggl.timer(description=description)

    def toggl_checker(self):
        toggl = skills.TogglManager()
        toggl.check_toggl_timer()

    def toggl_report(self, kind="chart", timely="weekly"):
        if kind is None:
            kind = 'chart'
        if timely is None:
            timely = 'weekly'
        toggl = skills.TogglManager()
        toggl.report(kind=kind, timely=timely)

    def maxim_nietzsche(self):
        maxim = skills.Maxim()
        maxim.nietzsche()

class RegisteredFuctions(object):
    class __List:
        def __init__(self):
            self.list = utils.DataHandler().read_file("skills.json")

    instance = None
    def __init__(self):
        if not RegisteredFuctions.instance:
            RegisteredFuctions.instance = RegisteredFuctions.__List()

    def __getattr__(self, name):
        return getattr(self.instance, name)
