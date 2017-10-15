
import pocket

from hbconfig import Config


class Pocket:

    def __init__(self):
        consumer_key = Config.open_api.pocket.CONSUMER_KEY
        access_token = Config.open_api.pocket.ACCESS_TOKEN

        self.api = pocket.Pocket(consumer_key, access_token)

    def add(self, url, tags: list=[]):
        tags = ",".join(tags)
        self.api.add(url, tags=tags)
