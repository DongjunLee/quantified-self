
from slacker import Slacker

import utils


class SlackerAdapter(object):

    def __init__(self):
        self.config = utils.Config()
        self.slacker = Slacker(self.config.slack['TOKEN'])
        self.data_handler = utils.DataHandler()

    def send_message(self, channel=None, text=None, attachments=None):
        if channel is None:
            channel = self.config.slack['DEFAULT_CHANNEL']
        r = self.slacker.chat.post_message(
            channel=channel,
            text=text,
            attachments=attachments,
            as_user=True)
        self.data_handler.edit_cache(('message', r.body))

    def update_message(self, channel=None, text=None, attachments=None):
        if text is None:
            text = ""

        cache = self.data_handler.read_cache()
        if 'send_message' in cache:
            cache_message = cache['message']
            ts = cache_message['ts']
            channel = cache_message['channel']
            self.slacker.chat.update(ts=ts, channel=channel, text=text,
                                     attachments=attachments, as_user=True)
        else:
            self.send_message(
                text="마지막 메시지에 대한 정보가 없습니다.",
                channel=channel,
                as_user=True)

    def file_upload(self, f_name, channel=None, title=None, comment=None):
        if channel is None:
            channel = self.config.slack['DEFAULT_CHANNEL']
        self.slacker.files.upload(
            f_name,
            channels=channel,
            title=title,
            initial_comment=comment)

    def start_real_time_messaging_session(self):
        response = self.slacker.rtm.start()
        return response.body['url']

    def get_bot_id(self):
        cache = self.data_handler.read_cache()
        if 'bot_id' in cache:
            return cache['bot_id']

        users = self.slacker.users.list().body['members']
        for user in users:
            if user['name'] == self.config.bot["BOT_NAME"].lower():
                bot_id = user['id']
                self.data_handler.edit_cache(('bot_id', bot_id))
                return bot_id
