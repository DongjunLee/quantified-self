
import twitter

from ..utils.config import Config



class TwitterManager:

    def __init__(self, slackbot=None):
        config = Config()
        self.api = twitter.Api(consumer_key=config.open_api["twitter"]["CONSUMER_KEY"],
                  consumer_secret=config.open_api["twitter"]["CONSUMER_SECRET"],
                  access_token_key=config.open_api["twitter"]["ACCESS_TOKEN_KEY"],
                  access_token_secret=config.open_api["twitter"]["ACCESS_TOKEN_SECRET"])

        if slackbot is None:
            self.slackbot = SlackerAdapter(channel=self.config.channel.get('FEED', '#general'))
        else:
            self.slackbot = slackbot

    def tweet(self, text: str) -> None:
        if len(text) > 140:
            text = text[:137] + "..."
        self.api.PostUpdate(text)

    def feed_tweet(self, feed: tuple) -> None:
        tweet_title = "#kino_bot, #feed"
        title, link, _ = feed

        if len(link) > 90:
            return

        remain_text_length = 140 - len(tweet_title) - len(link)

        if len(title) > remain_text_length:
            title = title[:remain_text_length - 5] + "..."

        self.tweet(f"{tweet_title}\n{title}\n{link}")

    def reddit_tweet(self, reddit: str) -> None:
        tweet_title = "#kino_bot, #reddit"

        self.tweet(f"{tweet_title}\n{reddit}")

