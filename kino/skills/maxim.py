
import random

import slack
import utils


class Maxim(object):

    def __init__(self, text=None):
        self.input = text
        self.slackbot = slack.SlackerAdapter()
        self.data_handler = utils.DataHandler()

    def nietzsche(self):
        maxim_list = self.data_handler.read_text("Nietzsche.txt").split("\n")
        choiced_maxim = random.choice(maxim_list)

        self.slackbot.send_message(text=choiced_maxim)
