import arrow
import numpy as np
import re
from dateutil import tz
from queue import Queue

from ..dialog.dialog_manager import DialogManager

from .arrow import ArrowUtil
from .data_handler import DataHandler
from .classes import Skill


class DataLoader(object):

    def __init__(self):
        pass

    def load_skill_queue(self, max_qsize=400):
        self.max_qsize = max_qsize
        return self.__read_file_then_convert()

    def make_data_set(self, q):
        data = list(q.queue)

        data_x = []
        data_y = []
        for x, y in data:
            data_x.append(x)
            data_y.append(y)
        return np.array(data_x), np.array(data_y)

    def __read_file_then_convert(self):
        data_handler = DataHandler()
        raw_data = data_handler.read_text("raw_data")

        q = RemoveOldDataQueue(self.max_qsize)

        skill_list = list(map(lambda x: x[0], Skill.classes))
        prev_line = ""
        for line in raw_data.split("\n"):
            if "raw input:" not in line:
                continue

            prev_func = len(Skill.classes)  # default value
            for idx, keyword_list in enumerate(skill_list):
                if all(k in prev_line for k in keyword_list):
                    prev_func = idx

            for idx, keyword_list in enumerate(skill_list):
                if all(k in line for k in keyword_list):
                    x = self.convert_data(line, prev_func)
                    if x is None:
                        continue

                    q.put_nowait((x, idx))
            prev_line = line
        return q

    def convert_data(self, line, prev_func):
        datetime_pattern = '\d+-\d+-\d+ \d+:\d+'
        r = re.findall(datetime_pattern, line)
        if len(r) == 0:
            return None

        t = arrow.get(r[0], tzinfo=tz.tzlocal())

        day_of_week = t.isoweekday()
        hour = int(t.format('HH'))
        minute = int(t.format('mm'))

        if day_of_week == 6 or day_of_week == 7:
            is_holiday = 1
        else:
            is_holiday = 0

        return np.array([day_of_week, hour, minute, prev_func,
                         is_holiday], dtype=np.int32)

    def make_X(self):
        day_of_week, hour, minute, is_holiday = ArrowUtil.convert_now2data()

        memory_text = DialogManager().get_memory(get_text=True)

        prev_func = len(Skill.classes)
        if memory_text is None:
            pass
        else:
            skill_list = list(map(lambda x: x[0], Skill.classes))
            for idx, keyword_list in enumerate(skill_list):
                if all(k in memory_text for k in keyword_list):
                    prev_func = idx

        return np.array(
            [[day_of_week, hour, minute, prev_func, is_holiday]], dtype=np.int32)

    def make_y(self, text):
        skill_list = list(map(lambda x: x[0], Skill.classes))
        for idx, keyword_list in enumerate(skill_list):
            if all(k in text for k in keyword_list):
                return idx
        return None


class RemoveOldDataQueue(Queue):

    def put_nowait(self, *args, **kwargs):
        if self.full():
            try:
                # oldest_data
                self.get()
            except Queue.Empty:
                pass
        Queue.put_nowait(self, *args, **kwargs)


class SkillData(object):
    class __Singleton:
        def __init__(self):
            data_loader = DataLoader()
            self.q = data_loader.load_skill_queue(max_qsize=400)

    instance = None

    def __init__(self):
        if not SkillData.instance:
            SkillData.instance = SkillData.__Singleton()

    def __getattr__(self, name):
        return getattr(self.instance, name)
