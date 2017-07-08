from trello import TrelloClient

from ..utils.config import Config


class TrelloManager(object):

    def __init__(self):
        config = Config()
        trello_config = config.open_api['trello']

        self.client = TrelloClient(
            api_key=trello_config['API_KEY'],
            api_secret=trello_config['API_SECRET'],
            token=trello_config['TOKEN']
        )
        self.board = self.client.get_board(trello_config['BOARD'])

    def get_list_by_name(self, name):
        for l in self.board.all_lists():
            if l.name == name:
                return l
        return None

    def add_card(self, list_name, card_name):
        l = self.get_list_by_name(list_name)
        l.add_card(card_name)

    def archive_all_cards(self, list_name):
        l = self.get_list_by_name(list_name)
        l.archive_all_cards()

    def clean_board(self):
        l_list = self.board.all_lists()
        for l in l_list:
            l.archive_all_cards()
