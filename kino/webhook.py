import arrow
from hbconfig import Config
import json

from .dialog.dialog_manager import DialogManager

from .slack.slackbot import SlackerAdapter
from .slack.template import MsgTemplate

from .utils.arrow import ArrowUtil
from .utils.data_handler import DataHandler
from .utils.logger import DataLogger
from .utils.state import State


class Webhook(object):

    def __init__(self):
        self.slackbot = SlackerAdapter()
        self.dialog_manager = DialogManager()
        self.data_handler = DataHandler()

    def relay(self, text):
        event = json.loads(text)

        """
        TODO : Customize your Webhook
        """

    def IN_OUT_handle(self, prev, event):
        if self.__is_error(prev, event):
            print("IFTTT error.")
            return

        if self.__is_phone_error(prev, event):
            pass
        else:
            action = event['action']
            time = ArrowUtil.get_action_time(event['time'])
            msg = event['msg']

            if getattr(self, "is_" + action)(time):
                self.slackbot.send_message(text=msg)
                self.data_handler.edit_record_with_category(
                    'activity', (action.lower(), str(time)))

    def __is_error(self, prev, event):
        if event['action'].startswith(
                "IN") and prev['action'].startswith("IN"):
            return True
        if event['action'].startswith(
                "OUT") and prev['action'].startswith("OUT"):
            return True
        return False

    def __is_phone_error(self, prev, event):
        THRESHOLD = 300
        if event['action'].startswith(
                "IN") and prev['action'].startswith("OUT"):
            if (ArrowUtil.get_action_time(
                    event['time']) - arrow.get(prev['time'])).seconds <= THRESHOLD:
                return True
        return False

    def is_IN_HOME(self, time):
        if ArrowUtil.is_between((20, 0), (24, 0), now=time) or \
                ArrowUtil.is_between((0, 0), (2, 0), now=time):
            return True
        else:
            return False

    def is_OUT_HOME(self, time):
        if ArrowUtil.is_between((7, 0), (9, 0), now=time):
            return True
        else:
            return False

    def is_IN_COMPANY(self, time):
        activity = self.data_handler.read_record().get('activity', None)
        if ArrowUtil.is_between((9, 0), (11, 30), now=time) and \
                activity.get('is_company', None) is None:
            return True
        else:
            return False

    def is_OUT_COMPANY(self, time):
        if ArrowUtil.is_between((17, 30), (23, 0), now=time):
            return True
        else:
            return False
