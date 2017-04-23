
import arrow

from .nlp.ner import NamedEntitiyRecognizer

from .skills.summary import Summary

from .slack.resource import MsgResource
from .slack.slackbot import SlackerAdapter

from .utils.arrow import ArrowUtil
from .utils.data_handler import DataHandler
from .utils.state import State


class DNDManager(object):

    def __init__(self):
        self.state = State()
        self.slackbot = slack.SlackerAdapter()
        self.data_handler = DataHandler()

    def call_is_holiday(self, dnd):
        Summary().record_holiday(dnd)
        if dnd:
            self.slackbot.send_message(text=MsgResource.HOLIDAY)
        else:
            self.slackbot.send_message(text=MsgResource.WEEKDAY)
