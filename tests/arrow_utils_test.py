
import arrow
import unittest

from hbconfig import Config
from kino.utils.arrow import ArrowUtil


class ArrowUtilTest(unittest.TestCase):

    def setUp(self):
        Config("config_example")
        print(Config)

    def test_is_weekday(self):

        mon = arrow.Arrow(2017, 8, 14).weekday()
        tue = arrow.Arrow(2017, 8, 15).weekday()
        wed = arrow.Arrow(2017, 8, 16).weekday()
        thu = arrow.Arrow(2017, 8, 17).weekday()
        fri = arrow.Arrow(2017, 8, 18).weekday()
        sat = arrow.Arrow(2017, 8, 19).weekday()
        sun = arrow.Arrow(2017, 8, 20).weekday()

        self.assertEqual(mon < 5, True)
        self.assertEqual(tue < 5, True)
        self.assertEqual(wed < 5, True)
        self.assertEqual(thu < 5, True)
        self.assertEqual(fri < 5, True)
        self.assertEqual(sat < 5, False)
        self.assertEqual(sun < 5, False)

    def test_is_today_day_of_week(self):
        today_day_of_week = arrow.now().weekday() + 1

        self.assertEqual(ArrowUtil.is_today_day_of_week([0]), True)
        self.assertEqual(ArrowUtil.is_today_day_of_week([today_day_of_week]), True)
        self.assertEqual(ArrowUtil.is_today_day_of_week([today_day_of_week, 4, 5]), True)
        self.assertEqual(ArrowUtil.is_today_day_of_week([10]), False)

        if ArrowUtil.is_weekday():
            self.assertEqual(ArrowUtil.is_today_day_of_week([8]), True)
        else:
            self.assertEqual(ArrowUtil.is_today_day_of_week([9]), True)

    def test_is_between(self):
        self.assertEqual(ArrowUtil.is_between((10, 0), (20, 0), now=arrow.Arrow(2017, 8, 14, 12, 0)), True)
        self.assertEqual(ArrowUtil.is_between((0, 0), (24, 0), now=arrow.Arrow(2017, 8, 14, 12, 0)), True)
        self.assertEqual(ArrowUtil.is_between((10, 0), (24, 0), now=arrow.Arrow(2017, 8, 14, 9, 0)), False)
        self.assertEqual(ArrowUtil.is_between((10, 0), (20, 0), now=arrow.Arrow(2017, 8, 14, 10, 0)), True)
        self.assertEqual(ArrowUtil.is_between((10, 0), (20, 0), now=arrow.Arrow(2017, 8, 14, 20, 0)), True)


    def test_get_curr_time_diff(self):
        start = arrow.Arrow(2017, 8, 14, 12, 0)
        end = arrow.Arrow(2017, 8, 14, 13, 0)

        self.assertEqual(ArrowUtil.get_curr_time_diff(start=start, stop=end), 60)
        self.assertEqual(ArrowUtil.get_curr_time_diff(start=start, stop=end, base_hour=True), 1)
