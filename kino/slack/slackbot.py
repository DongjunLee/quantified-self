
from slacker import Slacker

import utils

class SlackerAdapter(object):

    def __init__(self):
        self.config = utils.Config()
        self.slacker = Slacker(self.config.slack['TOKEN'])

    def send_message(self, channel=None, text=None, attachments=None):
        if channel is None:
            channel = self.config.slack['DEFAULT_CHANNEL']
        self.slacker.chat.post_message(channel=channel, text=text,
                                       attachments=attachments, as_user=True)

    def file_upload(self, f_name, channel=None, title=None, comment=None):
        if channel is None:
            channel = self.config.slack['DEFAULT_CHANNEL']
        self.slacker.files.upload(f_name, channels=channel, title=title
                                  , initial_comment=comment)

    def start_real_time_messaging_session(self):
        response = self.slacker.rtm.start()
        return response.body['url']

    def get_bot_id(self):
        users = self.slacker.users.list().body['members']
        for user in users:
            if user['name'] == self.config.bot["BOT_NAME"].lower():
                return user['id']
