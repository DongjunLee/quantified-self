import arrow
from dateutil import tz
import json

import nlp
import slack
from slack import MsgResource
import utils

class IFTTT(object):

    def __init__(self):
        self.slackbot = slack.SlackerAdapter()
        self.dialog_manager = nlp.DialogManager()
        self.arrow_util = utils.ArrowUtil()
        self.data_handler = utils.DataHandler()

    def relay(self, text):
        event = json.loads(text)

        prev_event = self.dialog_manager.get_action()
        nlp.State().do_action(event)

        if prev_event is None:
            self.slackbot.send_message(text=event['msg'])
            return

        action = event.get('action', '')
        if action.startswith("IN") or action.startswith("OUT"):
            self.IN_OUT_handle(prev_event, event)
        elif action.startswith("TODO"):
            self.TODO_handle(event)
        else:
            self.slackbot.send_message(text=event['msg'])

    def IN_OUT_handle(self, prev, event):
        if self.__is_error(prev, event):
            print("IFTTT error.")
            return

        if self.__is_phone_error(prev, event):
            self.slackbot.send_message(text=MsgResource.IN_OUT_ERROR)
        else:
            action = event['action']
            time = self.arrow_util.get_action_time(event['time'])
            msg = event['msg']

            if getattr(self, "is_" + action)(time):
                self.slackbot.send_message(text=msg)
                self.data_handler.edit_record_with_category('activity', (action.lower(), str(time)))

    def __is_error(self, prev, event):
        if event['action'].startswith("IN") and prev['action'].startswith("IN"):
            return True
        if event['action'].startswith("OUT") and prev['action'].startswith("OUT"):
            return True
        return False

    def __is_phone_error(self, prev, event):
        THRESHOLD = 300
        if event['action'].startswith("IN") and prev['action'].startswith("OUT"):
            if (self.arrow_util.get_action_time(event['time']) - arrow.get(prev['time'])).seconds <= THRESHOLD:
                return True
        return False

    def is_IN_HOME(self, time):
        if self.arrow_util.is_between((20,0), (24,0), now=time):
            return True
        else:
            return False

    def is_OUT_HOME(self, time):
        if self.arrow_util.is_between((7,0), (9,0), now=time):
            return True
        else:
            return False

    def is_IN_COMPANY(self, time):
        if self.arrow_util.is_between((9,0), (11,0), now=time):
            return True
        else:
            return False

    def is_OUT_COMPANY(self, time):
        if self.arrow_util.is_between((18,30), (23,0), now=time):
            return True
        else:
            return False

    def TODO_handle(self, event):
        msg = event['msg']
        self.slackbot.send_message(text=msg)

        if event['action'].endswith("COMPLATE"):
            self.dialog_manager.call_write_diary(msg)
            self.dialog_manager.call_do_exercise(msg)
