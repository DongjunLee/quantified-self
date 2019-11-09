# -*- coding: utf-8 -*-

import arrow
import json
import os


class DataHandler:
    def __init__(self):
        self.record_path = "../data/record/"

    def read_file(self, fname):
        text = self.read_text(fname)
        if text == "":
            return {}
        else:
            return json.loads(text)

    def read_text(self, path):
        try:
            with open(path, "rb") as infile:
                return infile.read().decode("utf-8")
        except BaseException:
            return ""

    def read_record(self, days=0, date_string=None):
        date = arrow.now().shift(days=int(days))
        if date_string is not None:
            date = arrow.get(date_string)
        fname = self.record_path + date.format("YYYY-MM-DD") + ".json"
        return self.read_file(fname)

    def read_acitivity(self, days=0):
        record_data = self.read_record(days=days)
        return record_data.get("activity", [])

    def read_summary(self, days=0):
        record_data = self.read_record(days=days)
        return record_data.get("summary", {})

