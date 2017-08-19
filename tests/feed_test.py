
import unittest

from kino.skills.feed import FeedNotifier


class FeedNotifierTest(unittest.TestCase):

    def test_feed_notify(self):
        feed = FeedNotifier()
        notify_data = feed.get_notify_list('News', ('NewsPeppermint', 'http://newspeppermint.com/feed/'))
        print(notify_data)
