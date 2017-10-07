
import arrow
from hbconfig import Config

from ..slack.resource import MsgResource
from ..slack.slackbot import SlackerAdapter
from ..slack.template import MsgTemplate
from ..slack.plot import Plot

from ..utils.arrow import ArrowUtil
from ..utils.data_handler import DataHandler
from ..utils.profile import Profile
from ..utils.score import Score
from ..utils.state import State


class Summary(object):

    def __init__(self, slackbot=None):
        self.data_handler = DataHandler()
        self.column_list = [
            "Attention",
            "Productive",
            "Happy",
            "Sleep",
            "REPEAT_TASK",
            "Total"]

        if Config.profile.personal:
            from ..utils.profile import Profile
            self.profile = Profile()

        if slackbot is None:
            self.slackbot = SlackerAdapter(
                channel=Config.slack.channel.get('REPORT', '#general'))
        else:
            self.slackbot = slackbot

    def record_write_diary(self):
        self.data_handler.edit_record(('Diary', True))

    def record_exercise(self):
        self.data_handler.edit_record(('Exercise', True))

    def record_bat(self):
        self.data_handler.edit_record(('BAT', True))

    def record_holiday(self, dnd):
        self.data_handler.edit_record(('Holiday', dnd))

    def is_holiday(self):
        record = self.data_handler.read_record()
        holiday = record.get('Holiday', None)
        if holiday is None:
            return not ArrowUtil.is_weekday()
        else:
            return holiday

    def check_go_to_bed(self):
        state = State()
        state.check()
        presence_log = state.current[state.SLEEP]
        if presence_log['presence'] == 'away':
            go_to_bed_time = arrow.get(presence_log['time'])
            self.data_handler.edit_record_with_category(
                'activity', ('go_to_bed', str(go_to_bed_time)))

    def check_commit_count(self):
        github = GithubManager()
        commit_count = github.commit(timely=-1)
        self.data_handler.edit_record(('Github', commit_count))
