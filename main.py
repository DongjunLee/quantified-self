# coding: UTF-8

from hbconfig import Config

from kino import KinoBot
from kino import prepare_feed_data
from kino import prepare_skill_data
from kino import register_skills


if __name__ == "__main__":
    register_skills()

    if Config.bot.get("SKILL_PREDICT", False):
        prepare_skill_data()
    if Config.bot.get("FEED_CLASSIFIER", False):
        prepare_feed_data()

    kino_bot = KinoBot()
    kino_bot.start_session(init=True)
