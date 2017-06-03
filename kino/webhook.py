import arrow
import json

from .dialog.dialog_manager import DialogManager

from .slack.resource import MsgResource
from .slack.slackbot import SlackerAdapter

from .skills.toggl import TogglManager
from .skills.summary import Summary

from .utils.arrow import ArrowUtil
from .utils.data_handler import DataHandler
from .utils.state import State



class Webhook(object):

    def __init__(self):
        self.slackbot = SlackerAdapter()
        self.dialog_manager = DialogManager()
        self.data_handler = DataHandler()

    def relay(self, text):
        event = json.loads(text)

        prev_event = self.dialog_manager.get_action()
        State().do_action(event)

        if prev_event is None:
            self.slackbot.send_message(text=event['msg'])
            return

        action = event.get('action', '')
        if action.startswith("IN") or action.startswith("OUT"):
            self.IN_OUT_handle(prev_event, event)
        elif action.startswith("TODO"):
            self.TODO_handle(event)
        elif action.startswith("KANBAN"):
            self.KANBAN_handle(event)
        else:
            self.slackbot.send_message(text=event['msg'])

    def IN_OUT_handle(self, prev, event):
        if self.__is_error(prev, event):
            print("IFTTT error.")
            return

        if self.__is_phone_error(prev, event):
            pass
            #self.slackbot.send_message(text=MsgResource.IN_OUT_ERROR)
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

    def TODO_handle(self, event):
        time = ArrowUtil.get_action_time(event['time'])
        minute = time.format("mm")

        msg = event['msg']
        if minute == "00":
            msg = "*기한이 지난* " + msg.replace("완료", "오늘로 갱신")
        else:
            if event['action'].endswith("COMPLATE"):
                if "일기" in msg:
                    Summary().record_write_diary()
                if "운동" in msg:
                    Summary().record_exercise()

        self.slackbot.send_message(text=msg)

    def KANBAN_handle(self, event):
        toggl_manager = TogglManager()

        action = event['action']
        description = event['msg']
        if action.endswith("DOING"):
            toggl_manager.timer(description=description)
        elif action.endswith("BREAK") or action.endswith("DONE"):
            toggl_manager.timer()
