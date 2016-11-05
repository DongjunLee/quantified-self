# -*- coding: utf-8 -*-

import functions
import slack
from slack import MsgResource

class Functions(object):

    def __init__(self):
        self.slackbot = slack.SlackerAdapter()
        self.registered = self.__registered_functions()

    def __registered_functions(self):
        function_dict = {}

        # Send Message
        send_message = {
            "params": ["*text", "channel"],
            "description": "해당 채널로 지정된 텍스트 메시지를 전송합니다.",
            "icon": MsgResource.SEND_MESSAGE_ICON
        }
        function_dict['send_message'] = send_message

        # Github Daily Commit
        daily_commit = {
            "params": ["channel"],
            "description": "일일커밋을 생활화하기 위해! Github commit 여부를 확인합니다.",
            "icon": MsgResource.DAILY_COMMIT_ICON
        }
        function_dict['daily_commit'] = daily_commit

        # Weather Daily Summary
        weather_current = {
            "params": ["channel"],
            "description": "현재 날씨 정보를 알려줍니다.",
            "icon": MsgResource.WEATHER_ICON
        }
        function_dict['weather_current'] = weather_current

        # Weather Daily Summary
        weather_daily = {
            "params": ["channel"],
            "description": "오늘의 날씨 정보를 알려줍니다.",
            "icon": MsgResource.WEATHER_ICON
        }
        function_dict['weather_summary'] = weather_daily

        # YouTube Downloader
        youtube_downloader = {
            "params": ["(passive)", "*YouTube Link"],
            "description": "YouTube 링크를 포함해서 메시지를 전송하면 Download Link를 생성합니다.",
            "icon": MsgResource.YOUTUBE_ICON
        }
        function_dict['youtube_downloader'] = youtube_downloader

        # Todoist - briefing
        today_briefing = {
            "params": ["channel"],
            "description": "Todoist에 등록된 일정들에 따라 하루 브리핑을 합니다.",
            "icon": MsgResource.TODOIST_ICON
        }
        function_dict['today_briefing'] = today_briefing


        # Todoist - summary
        today_summary = {
            "params": ["channel"],
            "description": "Todoist에 등록되어있는 일들이 처리되어 있는지 확인하고, 오늘 하루 요약을 합니다.",
            "icon": MsgResource.TODOIST_ICON
        }
        function_dict['today_summary'] = today_summary

        return function_dict

    def send_message(self, channel=None, text=None):
        self.slackbot.send_message(channel=channel, text=text)

    def daily_commit(self, channel=None):
        github = funtions.GithubManager()
        github.daily_commit_check(channel=channel)

    def weather_current(self, channel=None):
        weather = functions.Weather()
        weather.read(channel=channel, when='current')

    def weather_daily(self, channel=None):
        weather = functions.Weather()
        weather.read(channel=channel, when='daily')

    def today_briefing(self, channel=None):
        todoist = functions.TodoistManager()
        todoist.today_briefing(channel=channel)

    def today_summary(self, channel=None):
        todoist = functions.TodoistManager()
        todoist.today_summary(channel=channel)
