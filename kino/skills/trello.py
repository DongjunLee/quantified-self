from trello import TrelloClient
import random
from hbconfig import Config


class TrelloManager(object):

    def __init__(self):
        trello_config = Config.open_api.trello

        self.client = TrelloClient(
            api_key=trello_config.API_KEY,
            api_secret=trello_config.API_SECRET,
            token=trello_config.TOKEN
        )
        self.board = self.client.get_board(trello_config.BOARD)

    def get_list_by_name(self, name):
        for l in self.board.all_lists():
            if l.name == name:
                return l
        return None

    def get_random_card_name(self, list_name: str="Inbox"):
        l = self.get_list_by_name(list_name)
        if l is None or len(l.list_cards()) == 0:
            return None
        return random.choice(l.list_cards()).name

    def add_card(self, list_name: str, card_name):
        l = self.get_list_by_name(list_name)
        l.add_card(card_name)

    def archive_all_cards(self, list_name):
        l = self.get_list_by_name(list_name)
        l.archive_all_cards()

    def clean_board(self, except_list_name=None):
        l_list = self.board.all_lists()
        for l in l_list:
            if except_list_name is not None and l.name == except_list_name:
                pass
            else:
                l.archive_all_cards()
