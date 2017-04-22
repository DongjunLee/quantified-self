# -*- coding: utf-8 -*-

from ..functions import RegisteredFuctions

from ..slack.slackbot import SlackerAdapter
from ..slack.template import MsgTemplate



class SkillList(object):

    def __init__(self, text=None):
        self.slackbot = SlackerAdapter()
        self.template = MsgTemplate()

    def read(self):
        attachments = self.template.make_skill_template("", RegisteredFuctions().list)
        self.slackbot.send_message(attachments=attachments)
