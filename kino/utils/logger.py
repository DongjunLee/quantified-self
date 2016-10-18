import datetime
import logging
import os
import time

class Logger(object):
    class __Logger:
        def __init__(self):
            self._logger = logging.getLogger("crumbs")
            self._logger.setLevel(logging.INFO)
            formatter = logging.Formatter('[%(levelname)s|%(filename)s:%(lineno)s] %(asctime)s > %(message)s')

            now = datetime.datetime.now()
            timestamp = time.mktime(now.timetuple())

            dirname = './log'
            if not os.path.isdir(dirname):
                os.mkdir(dirname)
            fileHandler = logging.FileHandler(dirname + "/Kino_"+now.strftime("%Y-%m-%d %H:%M:%S")+".log")
            streamHandler = logging.StreamHandler()

            fileHandler.setFormatter(formatter)
            streamHandler.setFormatter(formatter)

            self._logger.addHandler(fileHandler)
            self._logger.addHandler(streamHandler)

    instance = None
    def __init__(self):
        if not Logger.instance:
            Logger.instance = Logger.__Logger()

    def get_logger(self):
        return self.instance._logger
