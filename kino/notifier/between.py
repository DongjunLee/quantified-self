# -*- coding: utf-8 -*-

from slack.template import MsgTemplate
from slack.slackbot import SlackerAdapter
from utils.data_handler import DataHandler

class Between(object):

    def __init__(self):
        self.slackbot = SlackerAdapter()
        self.data_handler = DataHandler()
        self.fname = "scheduler.json"
        self.template = MsgTemplate()

    def create(self, params):
        input_time_interval, input_description = params[0].split(" + ")
        input_between = {"time_interval": input_time_interval, "description": input_description, "color": self.__generate_color_code()}

        schedule_data, b_index = self.data_handler.read_json_then_add_data(self.fname, "between", input_between)

        attachments = self.template.make_schedule_template(
             "시간대가 등록되었습니다.",
            {b_index:input_between}
        )
        self.slackbot.send_message(attachments=attachments)

    def __generate_color_code(self):
        r = lambda: random.randint(0,255)
        color_code = '#%02X%02X%02X' % (r(),r(),r())
        return color_code

    def read(self, params):
        schedule_data = self.data_handler.read_file(self.fname)
        between_data = schedule_data.get('between', {})

        if between_data == {} or len(between_data) == 1:
            self.slackbot.send_message(text="등록된 시간대가 없습니다.")
        else:
            attachments = self.template.make_schedule_template("", between_data)
            self.slackbot.send_message(text="등록된 시간대 리스트입니다.", attachments=attachments)

    def update(self, params):
        b_index, input_time_interval, input_description = params[0].split(" + ")
        input_between = {"time_interval": input_time_interval, "description": input_description}

        result = self.data_handler.read_json_then_edit_data(self.fname, "between", b_index, input_between)

        if result == "sucess":
            attachments = self.template.make_schedule_template(
                "시간대가 변경되었습니다.",
                {b_index:input_between}
            )
            self.slackbot.send_message(attachments=attachments)
        else:
            self.slackbot.send_message(text="에러가 발생하였습니다.")

    def delete(self, params):
        b_index = params[0]

        self.data_handler.read_json_then_delete(self.fname, "between", b_index)
        self.slackbot.send_message(text="시간대가 삭제되었습니다.")
