# -*- coding: utf-8 -*-

import datetime

from utils.data_handler import DataHandler


class Config(object):
    class __Config:
        def __init__(self):
            config = DataHandler().read_file("config.json")

            self.bot = config["bot"]
            self.slack = config["slack"]
            self.profile = config["profile"]
            self.open_api = config["open_api"]

    instance = None

    def __init__(self):
        if not Config.instance:
            Config.instance = Config.__Config()

    def __getattr__(self, name):
        return getattr(self.instance, name)
