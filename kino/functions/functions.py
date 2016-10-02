# -*- coding: utf-8 -*-

from slack.slackbot import SlackerAdapter
from utils.resource import MessageResource

class Functions(object):

    def __init__(self):
        self.slackbot = SlackerAdapter()
        self.registered = self.__registered_functions()

    def __registered_functions(self):
        function_dict = {}
        send_message = {
            "params": ["text", "channel"],
            "description": "해당 채널로 텍스트 메시지를 전송합니다.",
            "icon": MessageResource.SEND_MESSAGE_ICON
        }
        function_dict['send_message'] = send_message
        return function_dict

    def send_message(self, channel="#personal_assistant", text=None):
        self.slackbot.send_message(channel=channel, text=text)
