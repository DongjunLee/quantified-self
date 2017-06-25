from ..slack.slackbot import SlackerAdapter
from ..slack.resource import MsgResource
from ..slack.template import MsgTemplate

from ..utils.config import Config
from ..utils.data_handler import DataHandler


class Guide(object):

    def __init__(self, slackbot=None):
        self.template = MsgTemplate()
        self.config = Config()
        self.data_handler = DataHandler()

        if slackbot is None:
            self.slackbot = SlackerAdapter()
        else:
            self.slackbot = slackbot

    def help(self):
        attachments = self.template.make_help_template(
            self.__guide(), self.__example())
        self.slackbot.send_message(attachments=attachments)

    def __guide(self):
        return "\n".join(MsgResource.template[self.config.bot["LANG_CODE"]]["GUIDE_DETAIL"])

    def __example(self):
        return MsgResource.template[self.config.bot["LANG_CODE"]]["GUIDE_KEYWORD"]
