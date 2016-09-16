import json

from slack.route import MsgRouter

class SlackListener(object):

    def __init__(self):
        self.router = MsgRouter()

    def handle_only_message(self, msg):
        self.msg = json.loads(msg)

        msg_type = self.msg.get("type", None)
        if msg_type == "message":
            print(self.msg)
            self.router.route(self.msg)

    def __make_full_text(self):
        pass

    def __parse_attachments(self):
        pass


