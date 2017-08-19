import arrow
import json

from .dialog.dialog_manager import DialogManager

from .slack.slackbot import SlackerAdapter

from .skills.toggl import TogglManager
from .skills.summary import Summary

from .utils.arrow import ArrowUtil
from .utils.config import Config
from .utils.data_handler import DataHandler
from .utils.state import State


class Webhook(object):

    def __init__(self):
        self.config = Config()
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
            channel = None

            action_lower = action.lower()

            sns = ['tweet', 'twitter', 'facebook', 'instagram']
            feed = ['feed', 'reddit']

            if any([s for s in sns if s in action_lower]):
                channel = self.config.channel['SNS']
            elif any([f for f in feed if f in action_lower]):
                channel = self.config.channel['FEED']
            self.slackbot.send_message(
                text=event['msg'], channel=channel, giphy=False)

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

    def TODO_handle(self, event):
        time = ArrowUtil.get_action_time(event['time'])
        msg = event['msg']

        activity_data = self.data_handler.read_record().get('activity', {})
        wake_up_time = arrow.get(activity_data.get('wake_up', None))

        if time.format("HH:mm") == wake_up_time.format("HH:mm"):
            msg = "*기한이 지난* " + msg.replace("완료", "오늘로 갱신")
        else:
            if event['action'].endswith("COMPLATE"):
                if "일기" in msg:
                    Summary().record_write_diary()
                if "운동" in msg:
                    Summary().record_exercise()
                if "BAT" in msg:
                    Summary().record_bat()

        self.slackbot.send_message(
            text=msg, channel=self.config.channel['TASK'])

    def KANBAN_handle(self, event):
        toggl_manager = TogglManager()

        action = event['action']
        description = event['msg']
        if action.endswith("DOING"):
            toggl_manager.timer(
                description=description,
                doing=True,
                done=False)
        elif action.endswith("BREAK"):
            toggl_manager.timer(doing=False, done=False)
        elif action.endswith("DONE"):
            toggl_manager.timer(doing=False, done=True)
