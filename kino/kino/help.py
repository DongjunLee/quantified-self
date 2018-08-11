from ..slack.slackbot import SlackerAdapter
from ..slack.resource import MsgResource
from ..slack.template import MsgTemplate

from ..utils.data_handler import DataHandler


class Guide(object):
    def __init__(self, slackbot=None):
        self.data_handler = DataHandler()

        if slackbot is None:
            self.slackbot = SlackerAdapter()
        else:
            self.slackbot = slackbot

    def help(self):
        attachments = MsgTemplate.make_help_template(
            self.__guide(), self.__keyword_list()
        )
        self.slackbot.send_message(attachments=attachments)

    def help_keyword(self):
        attachments = MsgTemplate.make_help_template(
            MsgResource.GUIDE_KEYWORD, self.__keyword_list()
        )
        self.slackbot.send_message(attachments=attachments)

    def __guide(self):
        return "\n".join(MsgResource.template[self.slackbot.lang_code]["GUIDE_DETAIL"])

    def __keyword_list(self):
        return MsgResource.template[self.slackbot.lang_code]["GUIDE_KEYWORD_LIST"]
