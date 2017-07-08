
from ..skills.summary import Summary

from ..slack.resource import MsgResource
from ..slack.slackbot import SlackerAdapter



class DoNotDisturbManager(object):

    def __init__(self):
        self.slackbot = SlackerAdapter()

    def call_is_holiday(self, dnd):
        Summary().record_holiday(dnd)
        if dnd:
            self.slackbot.send_message(text=MsgResource.HOLIDAY)
        else:
            self.slackbot.send_message(text=MsgResource.WEEKDAY)
