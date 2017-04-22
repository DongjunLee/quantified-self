
import arrow

from .dialog_manager import DialogManager

from ..nlp.ner import NamedEntitiyRecognizer

from ..skills.predictor import Predictor
from ..skills.summary import Summary
from ..skills.weather import Weather

from ..slack.resource import MsgResource
from ..slack.slackbot import SlackerAdapter

from ..utils.arrow import ArrowUtil
from ..utils.data_handler import DataHandler
from ..utils.state import State


class PreseneManager(object):

    def __init__(self):
        self.state = State()
        self.slackbot = SlackerAdapter()
        self.data_handler = DataHandler()
        self.dialog_manager = DialogManager()

    def check_wake_up(self, presence):
        record = self.data_handler.read_record()
        if 'wake_up' in record.get('activity', {}):
            return

        state = State()
        state.check()
        presence_log = state.current[state.SLEEP]
        if (ArrowUtil.is_between((6, 0), (11, 0)) and
                presence_log['presence'] == 'away' and presence == 'active'):
            self.slackbot.send_message(text=MsgResource.GOOD_MORNING)

            is_holiday = ArrowUtil.is_weekday() == False
            self.call_is_holiday(is_holiday)

            activity = record.get('activity', {})
            go_to_bed_time = arrow.get(activity.get('go_to_bed', None))

            wake_up_time = arrow.now()
            self.data_handler.edit_record_with_category(
                'activity', ('wake_up', str(wake_up_time)))

            sleep_time = (wake_up_time - go_to_bed_time).seconds / 60 / 60
            sleep_time = round(sleep_time * 100) / 100

            self.data_handler.edit_record(('Sleep', str(sleep_time)))

            self.slackbot.send_message(
                text=MsgResource.SLEEP_TIME(
                    go_to_bed_time.format("HH:mm"),
                    wake_up_time.format("HH:mm"),
                    str(sleep_time)))

            weather = Weather()
            weather.forecast(timely="daily")
            weather.air_quality()

    def check_flow(self, presence):
        if presence == "active":
            flow = self.dialog_manager.get_flow(is_raw=True)
            if flow.get('class', None) == "skills/Happy":
                self.slackbot.send_message(text=MsgResource.FLOW_HAPPY)

    def check_predictor(self, presence):
        flow = self.dialog_manager.get_flow(is_raw=True)
        flow_class = flow.get('class', None)
        if presence == "active" and flow_class is None:
            predictor = Predictor()
            predictor.predict_skill()
