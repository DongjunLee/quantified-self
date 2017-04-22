
from .slack.slackbot import SlackerAdapter
from .slack.template import MsgTemplate



class FunctionManager(object):

    def __init__(self):
        self.slackbot = SlackerAdapter()
        self.template = MsgTemplate()

    def read(self):
        attachments = self.template.make_skill_template("", self.functions)
        self.slackbot.send_message(attachments=attachments)

