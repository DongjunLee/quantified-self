import requests

import slack
from slack import MsgResource
import utils

class Naver(object):

    def __init__(self):
        self.config = utils.Config()
        self.slackbot = slack.SlackerAdapter()
        self.headers = {
            "X-Naver-Client-Id": self.config.open_api['naver']['CLIENT_ID'],
            "X-Naver-Client-Secret": self.config.open_api['naver']['CLIENT_SECRET']
        }

    def translate(self, text, source="en", target="ko"):
        if type(text) == list:
            text = " ".join(text)

        url = "https://openapi.naver.com/v1/language/translate"
        json = {
            "source": source,
            "target": target,
            "text": text
        }
        r = requests.post(url, json=json, headers=self.headers)
        if r.status_code == 200:
            result = r.json()['message']['result']['translatedText']
            self.slackbot.send_message(text=MsgResource.TRANSLATED_TEXT(result))
        else:
            self.slackbot.send_message(text=MsgResource.ERROR)
