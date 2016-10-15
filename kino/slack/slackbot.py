import os

from slacker import Slacker
from utils.config import Config

class SlackerAdapter(object):

    def __init__(self):
        self.config = Config()
        self.slacker = Slacker(self.config.kino['SLACK_BOT_TOKEN'])

    def send_message(self, channel=None, text=None, attachments=None):
        if channel is None:
            channel = self.config.kino['DEFAULT_CHANNEL']
        self.slacker.chat.post_message(channel=channel, text=text,
                                       attachments=attachments, as_user=True)

    def start_real_time_messaging_session(self):
        response = self.slacker.rtm.start()
        return response.body['url']

    def get_bot_id(self):
        users = self.slacker.users.list().body['members']
        for user in users:
            if user['name'] == "kino":
                return user['id']
