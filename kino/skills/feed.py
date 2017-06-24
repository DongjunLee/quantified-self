import arrow
import re
import feedparser

from ..slack.resource import MsgResource
from ..slack.slackbot import SlackerAdapter
from ..slack.template import MsgTemplate

from ..utils.data_handler import DataHandler
from ..utils.config import Config
from ..utils.logger import Logger




class FeedNotifier:

    def __init__(self, slackbot=None):
        data_handler = DataHandler()
        self.feed_list = data_handler.read_feeds()

        self.config = Config()
        self.thresh_hold = self.config.profile['feed']['INTERVAL'] * 60
        self.template = MsgTemplate()

        if slackbot is None:
            self.slackbot = SlackerAdapter(channel=self.config.channel['FEED'])
        else:
            self.slackbot = slackbot

    def notify_all(self):
        noti_list = []
        for f in self.feed_list:
            noti_list += self.notify(f)

        for feed in noti_list:
            attachments = self.template.make_feed_template(feed)
            self.slackbot.send_message(attachments=attachments)

    def notify(self, feed_url):
        noti_list = []

        feed = feedparser.parse(feed_url)
        for e in feed.entries:
            e_updated_date = arrow.get(e.updated_parsed)

            if (arrow.now() - e_updated_date).seconds < self.thresh_hold:
                noti_list.append((e.title, e.link, self.__remove_tag(e.description)))
        return noti_list

    def __remove_tag(self, text):
        text = re.sub('<.+?>', '', text, 0, re.I|re.S)
        text = re.sub('&nbsp;|\t|\r|', '', text)
        return text
