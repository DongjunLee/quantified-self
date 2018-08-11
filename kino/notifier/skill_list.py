# -*- coding: utf-8 -*-

from ..functions import RegisteredFuctions

from ..slack.slackbot import SlackerAdapter
from ..slack.template import MsgTemplate


class SkillList(object):
    def __init__(self, text=None, slackbot=None):
        if slackbot is None:
            self.slackbot = SlackerAdapter()
        else:
            self.slackbot = slackbot

    def read(self):
        attachments = MsgTemplate.make_skill_template("", RegisteredFuctions().list)
        self.slackbot.send_message(attachments=attachments)
