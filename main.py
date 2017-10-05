# coding: UTF-8

from kino import KinoBot
from kino import write_skills


if __name__ == "__main__":
    write_skills()

    kino_bot = KinoBot()
    kino_bot.start_session()
