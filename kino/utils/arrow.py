import arrow
import datetime
from dateutil import tz


class ArrowUtil(object):

    def __init__(self):
        pass

    @staticmethod
    def get_action_time(time):
        time_str = time.strip().replace('at', '')
        if time_str == "now":
            return arrow.get(arrow.now(), tzinfo=tz.tzlocal())
        else:
            return arrow.get(
                time_str,
                'MMMM D, YYYY  hh:mma',
                tzinfo=tz.tzlocal())

    @staticmethod
    def get_curr_time_diff(start=None, stop=None, base_hour=False):
        if isinstance(start, str):
            start = arrow.get(start)
        if isinstance(stop, str):
            stop = arrow.get(stop)

        if stop is None:
            stop = arrow.utcnow()

        diff = (stop - start).seconds / 60
        if base_hour:
            return round(diff / 60 * 100) / 100
        else:
            return int(diff)

    @staticmethod
    def is_between(start_time, end_time, now=None):
        if start_time is None and end_time is None:
            return True

        if now is None:
            now = datetime.datetime.now()

        start_h, start_m = start_time
        end_h, end_m = end_time

        if end_h == 24 and end_m == 0:
            end_h = 23
            end_m = 59

        start = now.replace(
            hour=start_h,
            minute=start_m,
            second=0,
            microsecond=0)
        end = now.replace(hour=end_h, minute=end_m, second=0, microsecond=0)
        if (start < now < end):
            return True
        else:
            return False

    @staticmethod
    def is_weekday():
        t = arrow.now()
        day_of_week = t.weekday()
        if day_of_week < 5:
            return True
        else:
            return False

    @staticmethod
    def convert_now2data():
        now = arrow.now()
        day_of_week = now.isoweekday()
        hour = int(now.format('HH'))
        minute = int(now.format('mm'))
        is_holiday = not ArrowUtil.is_weekday()

        return (day_of_week, hour, minute, is_holiday)

    @staticmethod
    def is_today_day_of_week(day_of_week):
        if day_of_week == [0]:
            return True

        now = arrow.now()
        today_day_of_week = now.weekday() + 1

        day_of_week = list(map(lambda x: int(x), day_of_week))
        if today_day_of_week in day_of_week:
            return True
        elif len(day_of_week) == 1:
            value = day_of_week[0]
            if value == 8 and ArrowUtil.is_weekday():
                return True
            elif value == 9 and not ArrowUtil.is_weekday():
                return True
        else:
            return False

