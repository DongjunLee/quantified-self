
import unittest

from hbconfig import Config
from kino.skills.feed import FeedNotifier


class FeedNotifierTest(unittest.TestCase):

    def setUp(self):
        Config("config_example")
        print(Config)

    def test_feed_notify(self):
        feed = FeedNotifier()
        notify_data = feed.get_notify_list('News', ('NewsPeppermint', 'http://newspeppermint.com/feed/'))
        print(notify_data)
