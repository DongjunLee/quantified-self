
from ..slack.resource import MsgResource
from ..slack.slackbot import SlackerAdapter


class DoNotDisturbManager(object):
    def __init__(self):
        self.slackbot = SlackerAdapter()

    def focus(self, dnd=None):
        if dnd.get("dnd_enabled", None):
            self.slackbot.send_message(text=MsgResource.FOCUS)
        else:
            self.slackbot.send_message(text=MsgResource.FOCUS_FINISH)
