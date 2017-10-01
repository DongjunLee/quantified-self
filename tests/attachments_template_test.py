import unittest

from hbconfig import Config
from kino.slack.template import MsgTemplate


class MsgTemplateTest(unittest.TestCase):

    def setUp(self):
        Config("config_example")
        print(Config)

    def test_schedule(self):
        attachments = MsgTemplate.make_schedule_template("pretext", {})
        self.assertEqual(isinstance(attachments, list), True)

    def test_skill(self):
        attachments = MsgTemplate.make_skill_template("pretext", {})
        self.assertEqual(isinstance(attachments, list), True)

    def test_help(self):
        attachments = MsgTemplate.make_help_template("guide", {})
        self.assertEqual(isinstance(attachments, list), True)

    def test_giphy(self):
        attachments = MsgTemplate.make_giphy_template("query", "url")
        self.assertEqual(isinstance(attachments, list), True)

    def test_weather(self):
        attachments = MsgTemplate.make_weather_template("address", "icon", "summary", "temperature")
        self.assertEqual(isinstance(attachments, list), True)

    def test_air_quality(self):
        data = {
            "cai": {
                "grade": "1",
                "value": "good",
                "description": "좋음"
                },
            "pm25": {}
        }
        attachments = MsgTemplate.make_air_quality_template("station_name", data)
        self.assertEqual(isinstance(attachments, list), True)

    def test_todoist(self):
        attachments = MsgTemplate.make_todoist_task_template([])
        self.assertEqual(isinstance(attachments, list), True)

    def test_feed(self):
        attachments = MsgTemplate.make_feed_template(("title", "link", "description"))
        self.assertEqual(isinstance(attachments, list), True)

    def test_bus(self):
        attachments = MsgTemplate.make_bus_stop_template({})
        self.assertEqual(isinstance(attachments, list), True)

    def test_summary(self):
        data = {
                "Color": "RED",
                "Total": "90"
                }
        attachments = MsgTemplate.make_summary_template(data)
        self.assertEqual(isinstance(attachments, list), True)
