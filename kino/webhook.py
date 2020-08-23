import arrow
from hbconfig import Config
import json

from .dialog.dialog_manager import DialogManager

from .slack.slackbot import SlackerAdapter
from .slack.template import MsgTemplate

from .skills.toggl import TogglManager
from .skills.twitter import TwitterManager
from .skills.summary import Summary

from .utils.arrow import ArrowUtil
from .utils.data_handler import DataHandler
from .utils.logger import DataLogger
from .utils.state import State


class Webhook(object):
    def __init__(self):
        self.slackbot = SlackerAdapter()
        self.dialog_manager = DialogManager()
        self.data_handler = DataHandler()

        self.feed_logger = DataLogger("feed").get_logger()
        self.pocket_logger = DataLogger("pocket").get_logger()

    def relay(self, text):
        event = json.loads(text)

        prev_event = self.dialog_manager.get_action()
        State().do_action(event)

        if prev_event is None:
            self.slackbot.send_message(text=event["msg"])
            return

        action = event.get("action", "")
        if action.startswith("IN") or action.startswith("OUT"):
            self.IN_OUT_handle(prev_event, event)
        elif action.startswith("TODO"):
            self.TODO_handle(event)
        elif action.startswith("KANBAN"):
            self.KANBAN_handle(event)
        elif action.startswith("POCKET"):
            self.POCKET_handle(event)
        else:
            channel = None

            action_lower = action.lower()

            sns = ["tweet", "twitter", "facebook", "instagram"]
            feed = ["feed", "reddit"]
            relay_message = event["msg"]

            if any([s for s in sns if s in action_lower]):
                channel = Config.slack.channel.get("SNS", "#general")
            elif any([f for f in feed if f in action_lower]):
                channel = Config.slack.channel.get("FEED", "#general")

                header, content = relay_message.split("\n\n")
                subreddit, title, link = header.split("\n")

                subreddit = subreddit.strip()
                title = title.strip()
                link = link.strip()
                link = link.replace("<", "")
                link = link.replace(">", "")

                feed = (subreddit, title, link)

                twitter = TwitterManager()
                twitter.reddit_tweet(feed)

                # save feed train data
                self.feed_logger.info(
                    json.dumps({"category": subreddit, "title": title})
                )

                title = f"{subreddit} Hot Post\n{title}"
                content = f"Link: {link}\n{content}"

                attachments = MsgTemplate.make_feed_template((title, link, content))
                self.slackbot.send_message(attachments=attachments, channel=channel)
                return

            self.slackbot.send_message(text=relay_message, channel=channel, giphy=False)

    def IN_OUT_handle(self, prev, event):
        if self.__is_error(prev, event):
            print("IFTTT error.")
            return

        if self.__is_phone_error(prev, event):
            pass
        else:
            action = event["action"]
            time = ArrowUtil.get_action_time(event["time"])
            msg = event["msg"]

            if getattr(self, "is_" + action)(time):
                self.slackbot.send_message(text=msg)
                self.data_handler.edit_record_with_category(
                    "activity", (action.lower(), str(time))
                )

    def __is_error(self, prev, event):
        if event["action"].startswith("IN") and prev["action"].startswith("IN"):
            return True
        if event["action"].startswith("OUT") and prev["action"].startswith("OUT"):
            return True
        return False

    def __is_phone_error(self, prev, event):
        THRESHOLD = 300
        if event["action"].startswith("IN") and prev["action"].startswith("OUT"):
            if (
                ArrowUtil.get_action_time(event["time"]) - arrow.get(prev["time"])
            ).seconds <= THRESHOLD:
                return True
        return False

    def is_IN_HOME(self, time):
        if ArrowUtil.is_between((20, 0), (24, 0), now=time) or ArrowUtil.is_between(
            (0, 0), (2, 0), now=time
        ):
            return True
        else:
            return False

    def is_OUT_HOME(self, time):
        if ArrowUtil.is_between((7, 0), (9, 0), now=time):
            return True
        else:
            return False

    def is_IN_COMPANY(self, time):
        activity = self.data_handler.read_record().get("activity", None)
        if (
            ArrowUtil.is_between((9, 0), (11, 30), now=time)
            and activity.get("is_company", None) is None
        ):
            return True
        else:
            return False

    def is_OUT_COMPANY(self, time):
        if ArrowUtil.is_between((17, 30), (23, 0), now=time):
            return True
        else:
            return False

    def TODO_handle(self, event):
        time = ArrowUtil.get_action_time(event["time"])
        msg = event["msg"]

        activity_data = self.data_handler.read_record().get("activity", {})
        wake_up_time = arrow.get(activity_data.get("wake_up", None))

        if time.format("HH:mm") == wake_up_time.format("HH:mm"):
            msg = "*기한이 지난* " + msg.replace("완료", "오늘로 갱신")
        else:
            if event["action"].endswith("COMPLATE"):
                if "일기" in msg:
                    Summary().record_write_diary()
                if "운동" in msg:
                    Summary().record_exercise()
                if "BAT" in msg:
                    Summary().record_bat()
                if "Blog" in msg:
                    Summary().record_blog()

        self.slackbot.send_message(
            text=msg, channel=Config.slack.channel.get("TASK", "#general")
        )

    def KANBAN_handle(self, event):
        toggl_manager = TogglManager()

        action = event["action"]
        description = event["msg"]
        if action.endswith("DOING"):
            toggl_manager.timer(description=description, doing=True, done=False)
        elif action.endswith("BREAK"):
            toggl_manager.timer(doing=False, done=False)
        elif action.endswith("DONE"):
            toggl_manager.timer(doing=False, done=True)

    def POCKET_handle(self, event):
        self.pocket_logger.info(json.dumps({"title": event["msg"]}))
