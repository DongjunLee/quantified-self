import random

from hbconfig import Config

from ..utils.data_handler import DataHandler


class MsgResourceType(type):
    class __MsgResource:

        def __init__(self):
            data_handler = DataHandler()

            self.template = data_handler.read_template()
            self.pool = {}

        def set_lang_code(self, lang_code):
            if lang_code in self.template.keys():
                self.lang_code = lang_code
            else:
                self.lang_code = Config.bot.LANG_CODE

        def __getattr__(self, name):
            self.pool[name] = {}

            message = self.template[Config.bot.LANG_CODE].get(
                name, "empty")
            if isinstance(message, list):
                message = random.choice(message)

            def wrapper(*args, **kwargs):
                self.pool[name] = {"args": args, "kwargs": kwargs}
                return "{" + name + "}"

            if isinstance(
                    message, dict) or (
                    "{" in message and "}" in message):
                return wrapper
            else:
                return "{" + name + "}"

        def to_text(self, msg_name):
            name = msg_name[1:-1]
            m_args = self.pool[name].get("args", None)
            m_kwargs = self.pool[name].get("kwargs", None)

            message = self.template[self.lang_code].get(
                name, "MsgResource not exist.")
            if isinstance(message, list):
                message = random.choice(message)

            def find_nearest_number(num_list, num):
                num = int(num)
                num_list = list(map(lambda x: int(x), num_list))
                return str(min(num_list, key=lambda x: abs(x - num)))

            if m_args is not None and len(m_args) == 1:
                arg = m_args[0]
                if arg in message:
                    return message[arg]
                else:
                    return message[find_nearest_number(message.keys(), arg)]
            elif m_kwargs is not None:
                return message.format(**m_kwargs)
            else:
                return message

    instance = None

    def __new__(cls, *args, **kwargs):  # __new__ always a classmethod
        if not cls.instance:
            cls.instance = cls.__MsgResource()
        return cls.instance


class MsgResource(metaclass=MsgResourceType):
    pass
