# -*- coding: utf-8 -*-

from .data_handler import DataHandler


class Config(object):
    class __Config:
        def __init__(self):
            config = DataHandler().read_file("config.json")

            bot = {
                "LANG_CODE": "en"
            }

            self.bot = config.get("bot", bot)
            self.channel = config.get("channel", {})
            self.slack = config.get("slack", {})
            self.profile = config.get("profile", {})
            self.open_api = config.get("open_api", {})

    instance = None

    def __init__(self):
        if not Config.instance:
            Config.instance = Config.__Config()

    def __getattr__(self, name):
        return getattr(self.instance, name)
