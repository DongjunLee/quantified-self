
from ..skills.summary import Summary

from ..slack.resource import MsgResource
from ..slack.slackbot import SlackerAdapter


class DoNotDisturbManager(object):

    def __init__(self):
        self.slackbot = SlackerAdapter()

    def call_is_holiday(self, dnd=None, holiday=None):

        if dnd is None and holiday is not None:
            holiday = holiday
        elif dnd is not None and holiday is None:
            holiday = dnd['dnd_enabled']

        # TODO: {'dnd_enabled': True, 'next_dnd_start_ts': 1500711803, 'next_dnd_end_ts': 1500715403}
        # -> dirrenct action with diff_min
        Summary().record_holiday(holiday)
        if dnd:
            self.slackbot.send_message(text=MsgResource.HOLIDAY)
        else:
            self.slackbot.send_message(text=MsgResource.WEEKDAY)
