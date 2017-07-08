# -*- coding: utf-8 -*-

import datetime

from .data_handler import DataHandler


class Config(object):
    class __Config:
        def __init__(self):
            config = DataHandler().read_file("config.json")

            bot = {
                "LANG_CODE": "en"
            }

            self.bot = config.get("bot", bot)
            self.channel = config.get("channel", None)
            self.slack = config.get("slack", None)
            self.profile = config.get("profile", None)
            self.open_api = config.get("open_api", None)

    instance = None

    def __init__(self):
        if not Config.instance:
            Config.instance = Config.__Config()

    def __getattr__(self, name):
        return getattr(self.instance, name)
