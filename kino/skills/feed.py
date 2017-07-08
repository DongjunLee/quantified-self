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
        self.logger = Logger().get_logger()

        self.data_handler = DataHandler()
        self.feed_list = self.data_handler.read_feeds()

        self.config = Config()

        if slackbot is None:
            self.slackbot = SlackerAdapter(channel=self.config.channel['FEED'])
        else:
            self.slackbot = slackbot

    def notify_all(self):
        self.logger.info("Check feed_list")
        noti_list = []
        for f in self.feed_list:
            noti_list += self.notify(f)

        for feed in noti_list:
            attachments = MsgTemplate.make_feed_template(feed)
            self.slackbot.send_message(attachments=attachments)

    def notify(self, feed_url):
        cache_data = self.data_handler.read_cache()

        f = feedparser.parse(feed_url)
        f.entries = sorted(
            f.entries, key=lambda x: x.get(
                'updated_parsed', 0), reverse=True)

        noti_list = []
        if feed_url in cache_data:
            previous_update_date = arrow.get(cache_data[feed_url])
            for e in f.entries:
                e_updated_date = arrow.get(e.updated_parsed)
                if e_updated_date > previous_update_date:
                    noti_list.append(
                        (e.get(
                            'title', ''), e.get(
                            'link', ''), self.__remove_tag(
                            e.get(
                                'description', ''))))
        elif f.entries:
            e = f.entries[0]
            noti_list.append(
                (e.get(
                    'title', ''), e.get(
                    'link', ''), self.__remove_tag(
                    e.get(
                        'description', ''))))
        else:
            pass

        if f.entries:
            last_e = f.entries[0]
            last_updated_date = arrow.get(last_e.get('updated_parsed', None))
            self.data_handler.edit_cache((feed_url, str(last_updated_date)))
        return noti_list

    def __remove_tag(self, text):
        text = re.sub('<.+?>', '', text, 0, re.I | re.S)
        text = re.sub('&nbsp;|\t|\r|', '', text)
        return text
