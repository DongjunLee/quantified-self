import arrow
import json
import os
import numpy as np
import re
from dateutil import tz
from queue import Queue

from ..dialog.dialog_manager import DialogManager

from .arrow import ArrowUtil
from .data_handler import DataHandler
from .classes import Skill


class SkillDataLoader(object):
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
        datetime_pattern = "\d+-\d+-\d+ \d+:\d+"
        r = re.findall(datetime_pattern, line)
        if len(r) == 0:
            return None

        t = arrow.get(r[0], tzinfo=tz.tzlocal())

        day_of_week = t.isoweekday()
        hour = int(t.format("HH"))
        minute = int(t.format("mm"))

        if day_of_week == 6 or day_of_week == 7:
            is_holiday = 1
        else:
            is_holiday = 0

        return np.array(
            [day_of_week, hour, minute, prev_func, is_holiday], dtype=np.int32
        )

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
            [[day_of_week, hour, minute, prev_func, is_holiday]], dtype=np.int32
        )

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
            data_loader = SkillDataLoader()
            self.q = data_loader.load_skill_queue(max_qsize=400)

    instance = None

    def __init__(self):
        if not SkillData.instance:
            SkillData.instance = SkillData.__Singleton()

    def __getattr__(self, name):
        return getattr(self.instance, name)

    def reset(self):
        SkillData.instance = SkillData.__Singleton()


class FeedDataLoader:

    FALSE_LABEL = 0
    TRUE_LABEL = 1

    def __init__(self):
        self.data_handler = DataHandler()

    def load_data(self, fname):
        data = self.data_handler.read_log_data(fname)
        return data.split("\n")

    def make_train_set(self, feed, pocket):
        feed = self.map_str_to_dict(feed)
        pocket = self.map_str_to_dict(pocket)
        pocket_title = set(map(lambda p: p["title"].strip(), pocket))

        train_y = []
        for f in feed:
            if f["title"].strip() in pocket_title:
                train_y.append(self.TRUE_LABEL)
            else:
                train_y.append(self.FALSE_LABEL)

        train_X, category_ids = self.map_category2id(feed)
        train_X = np.array(train_X).reshape(len(feed), 1)

        return train_X, train_y, category_ids

    def map_str_to_dict(self, data):
        data_list = []
        for d in data:
            try:
                data_list.append(json.loads(d[d.index("> {") + 2 :]))
            except:
                print("Faild convert to dict", d)
        return data_list

    def map_category2id(self, feed):
        keys = set(map(lambda f: f["category"].strip(), feed))

        category_ids = {}
        for idx, key in enumerate(list(keys)):
            category_ids[key] = idx

        return (
            list(map(lambda f: category_ids[f["category"].strip()], feed)),
            category_ids,
        )


class FeedData(object):
    class __Singleton:
        def __init__(self):
            data_loader = FeedDataLoader()

            feed = data_loader.load_data("feed.log")
            pocket = data_loader.load_data("pocket.log")

            self.train_X, self.train_y, self.category_ids = data_loader.make_train_set(
                feed, pocket
            )

    instance = None

    def __init__(self):
        if not FeedData.instance:
            FeedData.instance = FeedData.__Singleton()

    def __getattr__(self, name):
        return getattr(self.instance, name)

    def reset(self):
        FeedData.instance = FeedData.__Singleton()
