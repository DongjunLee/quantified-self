import random

from ..utils.config import Config
from ..utils.data_handler import DataHandler




class MsgResourceType(type):
    class __MsgResource:

        def __init__(self):
            config = Config()
            data_handler = DataHandler()

            self.resource = data_handler.read_template(config.bot["LANG_CODE"])

        def __getattr__(self, name):
            message =  self.resource[name]
            if isinstance(message, list):
                message = random.choice(message)

            def wrapper(*args, **kwargs):

                def find_nearest_number(num_list, num):
                    num = int(num)
                    num_list = list(map(lambda x: int(x), num_list))
                    return str(min(num_list, key=lambda x:abs(x-num)))

                if len(args) == 1:
                    arg = args[0]
                    if arg in message:
                        return message[arg]
                    else:
                        return message[find_nearest_number(message.keys(), arg)]
                elif kwargs is not None:
                    return message.format(**kwargs)
                else:
                    return message

            if isinstance(message, dict) or ("{" in message and "}" in message):
                return wrapper
            else:
                return message

    instance = None

    def __new__(cls, *args, **kwargs): # __new__ always a classmethod
        if not cls.instance:
            cls.instance = cls.__MsgResource()
        return cls.instance


class MsgResource(metaclass=MsgResourceType):
    pass
