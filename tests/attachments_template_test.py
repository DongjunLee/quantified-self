import unittest

from kino.slack.template import MsgTemplate


class MsgTemplateTest(unittest.TestCase):

    def test_schedule(self):
        MsgTemplate.make_schedule_template("pretext", {})

    def test_skill(self):
        MsgTemplate.make_skill_template("pretext", {})

    def test_help(self):
        MsgTemplate.make_help_template("guide", {})

    def test_giphy(self):
        MsgTemplate.make_giphy_template("query", "url")

    def test_weather(self):
        MsgTemplate.make_weather_template("address", "icon", "summary", "temperature")

    def test_air_quality(self):
        data = {
            "cai": {
                "grade": "1",
                "value": "good",
                "description": "좋음"
                },
            "pm25": {}
        }
        MsgTemplate.make_air_quality_template("station_name", data)

    def test_todoist(self):
        MsgTemplate.make_todoist_task_template([])

    def test_feed(self):
        MsgTemplate.make_feed_template(("title", "link", "description"))

    def test_bus(self):
        MsgTemplate.make_bus_stop_template({})

    def test_summary(self):
        data = {
                "Color": "RED",
                "Total": "90"
                }
        MsgTemplate.make_summary_template(data)
