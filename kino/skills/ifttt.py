import json

import slack

class IFTTT(object):

    def __init__(self):
        self.slackbot = slack.SlackerAdapter()

    def relay(self, text):
        event = json.loads(text)
        self.slackbot.send_message(text=event['msg'])
