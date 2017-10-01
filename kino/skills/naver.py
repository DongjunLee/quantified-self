import requests
from hbconfig import Config

from ..slack.resource import MsgResource
from ..slack.slackbot import SlackerAdapter



class Naver(object):

    def __init__(self, slackbot=None):
        self.headers = {
            "X-Naver-Client-Id": Config.open_api.naver.CLIENT_ID,
            "X-Naver-Client-Secret": Config.open_api.naver.CLIENT_SECRET}

        if slackbot is None:
            self.slackbot = SlackerAdapter()
        else:
            self.slackbot = slackbot

    def translate(self, text, source="en", target="ko"):
        if isinstance(text, list):
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
            self.slackbot.send_message(
                text=MsgResource.TRANSLATED_TEXT(result=result))
        else:
            self.slackbot.send_message(text=MsgResource.ERROR)
