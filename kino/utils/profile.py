
from dateutil import tz
from hbconfig import Config

from .arrow import ArrowUtil
from .data_handler import DataHandler


class Profile(object):
    def __init__(self):
        profile = Config.profile
        self.personal = profile.get("personal", None)
        self.schedule = profile.get("schedule", None)
        self.location = profile.get("location", None)
        self.task = profile.get("task", None)
        self.score = profile.get("score", None)

    def get_schedule(self, keyword, parsed=False):
        if parsed:
            return self.__parse_during_time(self.schedule[keyword])
        else:
            return self.schedule[keyword]

    def __parse_during_time(self, during_text):
        start_time, end_time = during_text.split("~")
        return (self.__parse_time(start_time), self.__parse_time(end_time))

    def __parse_time(self, time_text):
        hour, minute = time_text.split(":")
        return (int(hour), int(minute))

    def get_location(self, station=False):
        if self.location is None:
            return "UNKNOWN"

        data_handler = DataHandler()
        record = data_handler.read_record()
        activity = record.get("activity", {})

        in_company = activity.get("in_company", None)
        out_company = activity.get("out_company", None)
        in_home = activity.get("in_home", None)

        is_work = False
        if self.personal:

            if in_company is not None:
                if out_company is None:
                    is_work = True
                elif in_home is not None:
                    is_work = False
                else:
                    diff = ArrowUtil.get_curr_time_diff(
                        start=out_company, base_hour=True
                    )
                    if diff > 1:
                        is_work = False
                    else:
                        is_work = True
            else:
                is_work = False

        else:
            is_work = True

        if is_work:
            if station:
                return self.location["WORK_PLACE_STATION_NAME"]
            else:
                return self.location["WORK_PLACE"]
        else:
            if station:
                return self.location["HOME_STATION_NAME"]
            else:
                return self.location["HOME"]

    def get_timezone(self):
        if self.location is None:
            return None
        if "TIMEZONE" not in self.location:
            return tz.tzlocal()

        return tz.gettz(self.location["TIMEZONE"])

    def get_task(self, keyword):
        return self.task[keyword]

    def get_score(self, keyword):
        return self.score[keyword]
