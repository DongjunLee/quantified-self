import os

from slacker import Slacker

class SlackerAdapter(object):

    def __init__(self):
        self.slacker = Slacker(os.environ['KINO_BOT_TOKEN'])

    def send_message(self, channel="#personal_assistant", text=None, attachments=None):
        self.slacker.chat.post_message(channel=channel, text=text,
                                       attachments=attachments, as_user=True)

    def start_real_time_messaging_session(self):
        response = self.slacker.rtm.start()
        return response.body['url']
