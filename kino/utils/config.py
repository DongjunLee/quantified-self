
from utils.data_handler import DataHandler

class Config(object):
    class __Config:
        def __init__(self):
            self.data_handler = DataHandler()
            self.fname = "config.json"

            config = self.__read_config()
            self.kino = config["kino"]
            self.github = config["github"]

        def __read_config(self):
            return self.data_handler.read_file(self.fname)

    instance = None
    def __init__(self):
        if not Config.instance:
            Config.instance = Config.__Config()

    def __getattr__(self, name):
        return getattr(self.instance, name)
