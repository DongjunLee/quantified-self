import arrow
import re
import feedparser
from hbconfig import Config

from ..slack.slackbot import SlackerAdapter
from ..slack.template import MsgTemplate

from ..utils.data_handler import DataHandler
from ..utils.logger import Logger
from ..utils.logger import DataLogger


class FeedNotifier:

    def __init__(self, slackbot: SlackerAdapter=None) -> None:
        self.logger = Logger().get_logger()
        self.feed_logger = DataLogger("feed").get_logger()

        self.data_handler = DataHandler()
        self.feeds = self.data_handler.read_feeds()

        if slackbot is None:
            self.slackbot = SlackerAdapter(channel=Config.slack.channel.get('FEED', "#general"))
        else:
            self.slackbot = slackbot

    def notify_all(self) -> None:
        self.logger.info("Check feed_list")
        noti_list = []
        for category, feed_list in self.feeds.items():
            for feed in feed_list:
                noti_list += self.get_notify_list(category, feed)

        for feed in noti_list:
            feed_header = feed[0].split("\n")
            self.feed_logger.info({"category": feed_header[0], "title": feed_header[1]})

            attachments = MsgTemplate.make_feed_template(feed)
            self.slackbot.send_message(attachments=attachments)


    def get_notify_list(self, category: str, feed: tuple) -> list:
        cache_data = self.data_handler.read_cache()

        feed_name, feed_url = feed
        f = feedparser.parse(feed_url)

        f.entries = sorted(
            f.entries, key=lambda x: x.get(
                'updated_parsed', 0), reverse=True)

        # get Latest Feed
        noti_list = []
        if feed_url in cache_data:
            previous_update_date = arrow.get(cache_data[feed_url])
            for e in f.entries:
                e_updated_date = arrow.get(e.updated_parsed)
                if e_updated_date > previous_update_date:
                    noti_list.append(self.__make_entry_tuple(category, e, feed_name))

        elif f.entries:
            e = f.entries[0]
            noti_list.append(self.__make_entry_tuple(category, e, feed_name))
        else:
            pass

        if f.entries:
            last_e = f.entries[0]
            last_updated_date = arrow.get(last_e.get('updated_parsed', None))
            self.data_handler.edit_cache((feed_url, str(last_updated_date)))

        # filter feeded entry link
        cache_entry_links = set(cache_data.get("feed_links", []))
        noti_list = list(filter(lambda e: e[1] not in cache_entry_links, noti_list))

        # Cache entry link
        for entry in noti_list:
            _, entry_link, _ = entry
            cache_entry_links.add(entry_link)
            self.data_handler.edit_cache(("feed_links", list(cache_entry_links)))

        return noti_list

    def __make_entry_tuple(self, category: str, entry: dict, feed_name: str) -> tuple:
        entry_title = f"[{category}] - {feed_name} \n" + entry.get('title', '')
        entry_link = entry.get('link', '')
        entry_description = f"Link : {entry_link} \n" + self.__remove_tag(entry.get('description', ''), entry_link)
        return (entry_title, entry_link, entry_description)

    def __remove_tag(self, text: str, entry_link: str) -> str:
        text = re.sub('<.+?>', '', text, 0, re.I | re.S)
        text = re.sub('&nbsp;|\t|\r|', '', text)
        text = re.sub(entry_link, '', text)
        return text
