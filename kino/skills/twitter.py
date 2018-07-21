
import twitter
from hbconfig import Config

from ..slack.slackbot import SlackerAdapter

from ..utils.data_handler import DataHandler
from ..utils.logger import Logger



class TwitterManager:

    MAX_KEEP = 50

    MAX_TEXT_LENGTH = 135
    MAX_LINK_LENGTH = 80

    HOME_TIMELINE_COUNT = 50
    FAVORITE_THRESHOLD = 50

    def __init__(self, slackbot=None):
        self.logger = Logger().get_logger()

        self.data_handler = DataHandler()

        self.api = twitter.Api(consumer_key=Config.open_api.twitter.CONSUMER_KEY,
                  consumer_secret=Config.open_api.twitter.CONSUMER_SECRET,
                  access_token_key=Config.open_api.twitter.ACCESS_TOKEN_KEY,
                  access_token_secret=Config.open_api.twitter.ACCESS_TOKEN_SECRET)

        if slackbot is None:
            self.slackbot = SlackerAdapter(channel=Config.slack.channel.get('SNS', '#general'))
        else:
            self.slackbot = slackbot

    def notify_popular_tweet(self):
        self.logger.info("Check popular tweet")
        cache_data = self.data_handler.read_cache()
        cache_tweet_ids = set(cache_data.get("tweet_ids", []))

        for tweet in self.get_popular_tweet():
            self.slackbot.send_message(text=f"*Popular Tweet*\n - :+1: ({tweet[3]}) {tweet[1]}: {tweet[2]}", giphy=False)
            cache_tweet_ids.add(tweet[0])
        self.data_handler.edit_cache(("tweet_ids", list(cache_tweet_ids)[-self.MAX_KEEP]))

    def get_popular_tweet(self):
        cache_data = self.data_handler.read_cache()
        cache_tweet_ids = set(cache_data.get("tweet_ids", []))

        tweets = []
        for r in self.api.GetHomeTimeline(count=self.HOME_TIMELINE_COUNT):
            if r.retweeted_status is not None:
                r = r.retweeted_status
            if r.favorite_count > 50 and r.id not in cache_tweet_ids:
                tweets.append((r.id, r.user.name, r.text, r.favorite_count))
        return tweets

    def tweet(self, text: str) -> None:
        if len(text) > self.MAX_TEXT_LENGTH:
            text = text[:self.MAX_TEXT_LENGTH - 3] + "..."
        try:
            self.api.PostUpdate(text)
        except BaseException as e:
            self.logger.error("tweet error: " + text)

    def feed_tweet(self, feed: tuple) -> None:
        tweet_title = "#kino_bot, #feed"
        title, link, _ = feed

        self.logger.info("tweet latest feed. title: " + title + " link: " + link)

        if len(link) > self.MAX_LINK_LENGTH:
            self.logger.info("Skip to tweet. Link length is too long. length: " +str(len(link)))
            return

        remain_text_length = self.MAX_TEXT_LENGTH - len(tweet_title) - len(link)

        if len(title) > remain_text_length:
            title = title[:remain_text_length - 3] + "..."

        self.tweet(f"{tweet_title}\n{title}\n{link}")

    def reddit_tweet(self, reddit: tuple) -> None:
        cache_data = self.data_handler.read_cache()
        cache_entry_links = set(cache_data.get("entry_links", []))

        subreddit, title, link = reddit
        if link in cache_entry_links:
            return

        subreddit = subreddit.replace("MachineLearning", "ml")

        tweet_title = "#kino_bot, #reddit_" + subreddit.lower()

        if len(link) > self.MAX_LINK_LENGTH:
            self.logger.info("Skip to tweet. Link length is too long. length: " +str(len(link)))
            return

        remain_text_length = self.MAX_TEXT_LENGTH - len(tweet_title) - len(link)

        if len(title) > remain_text_length:
            title = title[:remain_text_length - 3] + "..."

        self.tweet(f"{tweet_title}\n{title}\n{link}")

        cache_entry_links.add(link)
        self.data_handler.edit_cache(("feed_links", list(cache_entry_links)))
