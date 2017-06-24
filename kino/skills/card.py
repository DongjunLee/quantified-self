import arrow
import re

from ..slack.resource import MsgResource

from ..utils.data_handler import DataHandler
from ..utils.member import Member



class BusinessCard(object):

    def __init__(self, slackbot=None):
        self.fname = "card.json"
        self.data_handler = DataHandler()

        if slackbot is None:
            self.slackbot = SlackerAdapter()
        else:
            self.slackbot = slackbot

    def read_holder(self):
        card_data = self.data_handler.read_file(self.fname)
        holder_names = ", ".join(card_data.get("holder", []))
        holder_names = re.sub('([A-Z])+', r'\1-', holder_names)
        self.slackbot.send_message(text=MsgResource.CARD_HOLDER(names=holder_names))

    def read_history(self):
        card_data = self.data_handler.read_file(self.fname)
        historys = "\n - ".join(card_data.get("history", [])[-5:])
        self.slackbot.send_message(text=MsgResource.CARD_HISTORY(historys=historys))

    def forward(self, member):
        if member is None:
            self.slackbot.send_message(text=MsgResource.CARD_FORWARD_NONE)
            return
        elif len(member) > 2:
            self.slackbot.send_message(text=MsgResource.CARD_FORWARD_NONE)
            return

        if len(member) == 2:
            from_name = member[0]
            to_name = member[1]
        else: # len(member) == 1
            member_util = Member()
            from_name = member_util.get_name(self.slackbot.user)
            to_name = member[0]

        if from_name != to_name:
            card_data = self.data_handler.read_file(self.fname)

            holder_data = card_data.get("holder", [])

            if from_name not in holder_data:
                self.slackbot.send_message(text=MsgResource.NOT_CARD_HOLDER(from_name=from_name))
                return

            holder_data.remove(from_name)
            holder_data.append(to_name)

            history_data = card_data.get("history", [])
            history_data.append(arrow.now().format("YYYY-MM-DD HH:mm") + f": {from_name} -> {to_name}" )

            card_data["holder"] = holder_data
            card_data["history"] = history_data

            self.data_handler.write_file(self.fname, card_data)

        self.slackbot.send_message(text=MsgResource.CARD_FORWARD(from_name=from_name, to_name=to_name))
