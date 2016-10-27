
import random

from slack.slackbot import SlackerAdapter
from utils.data_handler import DataHandler

class Maxim(object):

    def __init__(self):
        self.slackbot = SlackerAdapter()
        self.data_handler = DataHandler()

    def nietzsche(self):
        maxim_list = self.data_handler.read_text("Nietzsche.txt").split("\n")
        choiced_maxim = random.choice(maxim_list)

        self.slackbot.send_message(text=choiced_maxim)
