
import unittest

from hbconfig import Config
from kino.listener import MsgListener


class MsgListenerTest(unittest.TestCase):
    def setUp(self):
        Config("config_example")
        print(Config)

    test_presence_msg = {"type": "presence_change", "presence": "away"}

    def test_is_presence(self):
        self.assertEqual(MsgListener().is_presence(self.test_presence_msg), True)

    test_message_msg = {"type": "message"}

    def test_is_message(self):
        self.assertEqual(MsgListener().is_message(self.test_message_msg), True)

    test_bot_msg1 = {"type": "message", "subtype": "bot_message"}

    test_bot_msg2 = {"type": "message", "bot_id": "testing"}

    test_bot_msg3 = {
        "type": "message",
        "subtype": "message_changed",
        "message": {"bot_id": "testing"},
    }

    def test_is_bot(self):
        self.assertEqual(MsgListener().is_bot(self.test_bot_msg1), True)
        self.assertEqual(MsgListener().is_bot(self.test_bot_msg2), True)
        self.assertEqual(MsgListener().is_bot(self.test_bot_msg3), True)

    test_direct_msg1 = {"type": "message", "channel": "D12981923"}

    test_direct_msg2 = {"type": "message", "channel": "Clajdflak"}

    test_direct_msg3 = {"type": "message", "channel": "Clajdflak", "text": "키노야"}

    def test_is_direct(self):
        pass
        # Can't test on Travis
        # self.assertEqual(MsgListener().is_direct(self.test_direct_msg1), True)
        # self.assertEqual(MsgListener().is_direct(self.test_direct_msg2), False)
        # self.assertEqual(MsgListener().is_direct(self.test_direct_msg3), True)

    test_dnd_msg1 = {"type": "dnd_updated_user", "dnd_status": "dnd_change"}

    def test_is_dnd_updated_user(self):
        self.assertEqual(MsgListener().is_dnd_updated_user(self.test_dnd_msg1), True)
