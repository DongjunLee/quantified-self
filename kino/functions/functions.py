# -*- coding: utf-8 -*-

from functions.github import GithubManager
from slack.slackbot import SlackerAdapter
from utils.resource import MessageResource

class Functions(object):

    def __init__(self):
        self.slackbot = SlackerAdapter()
        self.registered = self.__registered_functions()

    def __registered_functions(self):
        function_dict = {}

        # Send Message
        send_message = {
            "params": ["*text", "channel"],
            "description": "해당 채널로 텍스트 메시지를 전송합니다.",
            "icon": MessageResource.SEND_MESSAGE_ICON
        }
        function_dict['send_message'] = send_message

        # Github Daily Commit
        daily_commit = {
            "params": ["channel"],
            "description": "일일커밋을 생활화하기 위해! Github commit 여부를 확인합니다.",
            "icon": MessageResource.DAILY_COMMIT_ICON
        }
        function_dict['daily_commit'] = daily_commit

        return function_dict

    def send_message(self, channel=None, text=None):
        self.slackbot.send_message(channel=channel, text=text)

    def daily_commit(self, channel=None):
        github = GithubManager()
        github.daily_commit_check(channel=channel)

