import re

from ..slack.slackbot import SlackerAdapter

from ..utils.data_handler import DataHandler


class Member(object):

    def __init__(self):
        self.data_handler = DataHandler()
        self.slackbot = SlackerAdapter()

    def get_names(self, text):
        user_ids = self.__parse_user_ids(text)
        member_data = self.__get_member_data()

        user_names = list(map(lambda x: self.get_name(
            x, member_data=member_data), user_ids))
        user_names = list(
            filter(
                lambda x: x is not None and x.lower() != "no ki",
                user_names))
        return user_names

    def __parse_user_ids(self, text):
        pattern = "@U[0-9A-Z]+"
        result = re.findall(pattern, text)
        return list(map(lambda x: x[1:], result))

    def __get_member_data(self, is_write=False):
        cache_data = self.data_handler.read_cache()
        member_data = cache_data.get("member", None)

        if member_data is None or is_write:
            member_data = self.slackbot.get_users()
            self.data_handler.edit_cache(("member", member_data))
        return member_data

    def get_name(self, user_id, member_data=None):
        if member_data is None:
            member_data = self.__get_member_data()

        name = self.__get_name(user_id, member_data)
        if name is None:
            member_data = self.__get_member_data(is_write=True)
        return self.__get_name(user_id, member_data)

    def __get_name(self, user_id, member_data):
        for member in member_data:
            if user_id == member.get("id", ""):
                return member["profile"]["real_name"]
        return None
