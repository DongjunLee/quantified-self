
import random
import requests
import re
import types
from urllib.parse import urlencode, quote_plus

import langid
from slacker import Slacker

from .resource import MsgResource
from .template import MsgTemplate

from ..utils.config import Config
from ..utils.data_handler import DataHandler


class SlackerAdapter(object):

    def __init__(self, channel=None, user=None, input_text=None):
        self.config = Config()
        self.slacker = Slacker(self.config.slack['TOKEN'])
        self.channel = channel
        self.data_handler = DataHandler()

        self.user = user
        self.channel = channel

        if input_text is None:
            self.lang_code = self.config.bot["LANG_CODE"]
        else:
            self.lang_code = langid.classify(input_text)[0]

    def send_message(self, channel=None, text=None, attachments=None):
        if self.channel is None:
            self.channel = self.config.channel['DEFAULT']
        if channel is not None:
            self.channel = channel

        MsgResource.set_lang_code(self.lang_code)
        text = self.__message2text(text)

        if attachments is not None:
            attachments = self.attachment_message2text(attachments)

        gihpy_result = None
        random_num = random.randint(1, 100)
        if (text is not None and attachments is None) and \
                random_num > self.config.bot["GIPHY_THRESHOLD"]:
            gihpy = GiphyClient()
            gihpy_result = gihpy.search(text)

        if gihpy_result is None:
            r = self.slacker.chat.post_message(
                channel=self.channel,
                text=text,
                attachments=attachments,
                as_user=True)
            self.data_handler.edit_cache(('message', r.body))

    def attachment_message2text(self, d):
        if not isinstance(d, (dict, list)):
            return d
        if isinstance(d, list):
            return [ self.__message2text(v) for v in (self.attachment_message2text(v) for v in d)]
        return {k: self.__message2text(v) for k, v in ((k, self.attachment_message2text(v)) for k, v in d.items())}

    def __message2text(self, msg_text):
        if isinstance(msg_text, str):
            result = re.findall(r"\{[A-Z][A-Z_0-9]+\}", msg_text)
            if len(result) > 0:
                for r in result:
                    msg_text = msg_text.replace(r, MsgResource.to_text(r))
        return msg_text

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
        if self.channel is None:
            self.channel = self.config.channel['DEFAULT']
        if channel is not None:
            self.channel = channel

        comment = self.__message2text(comment)

        self.slacker.files.upload(
            f_name,
            channels=self.channel,
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

    def get_users(self):
        return self.slacker.users.list().body['members']



class GiphyClient:

    def __init__(self, limit=10):
        self.config = Config()

        self.base_url = "http://api.giphy.com/v1/gifs/"
        self.api_key = self.config.open_api["giphy"]["TOKEN"]
        self.limit = limit

        self.slackbot = SlackerAdapter()
        self.template = MsgTemplate()

    def search(self, q):
        payload = {'q': q, 'api_key': self.api_key, 'limit': self.limit, 'lang': langid.classify(q)[0]}
        query = urlencode(payload, quote_via=quote_plus)

        r = requests.get(f"{self.base_url}search?{query}")
        if r.status_code == 200:
            result = r.json()['data']
            if len(result) == 0:
                return None

            choiced_gif = random.choice(result)
            url = choiced_gif['images']['downsized']['url']
            attachments = self.template.make_giphy_template(q, url)

            self.slackbot.send_message(attachments=attachments)
            return True
        else:
            return None
