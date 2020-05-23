# -*- coding: utf-8 -*-

import arrow
import boto3
import json


class DataHandler:
    def __init__(self):
        self.s3_client = boto3.client('s3')
        self.record_path = "../data/record/"

    def read_file(self, fname):
        text = self.read_text(fname)
        if text == "":
            return None
        else:
            return json.loads(text)

    def read_text(self, path):
        try:
            with open(path, "rb") as infile:
                return infile.read().decode("utf-8")
        except BaseException:
            return ""

    def read_record(self, days=0, date_string=None, redownload=False):
        date = arrow.now().shift(days=int(days))
        if date_string is not None:
            date = arrow.get(date_string)

        basename = date.format("YYYY-MM-DD") + ".json"
        file_path = self.record_path + basename
        record = self.read_file(file_path)
        if record is None or redownload is True:
            year_str = date.format("YYYY")
            try:
                self.s3_client.download_file("kino-records", f"{year_str}/{basename}", file_path)
            except BaseException:
                return {}

        return self.read_file(file_path)

    def read_acitivity(self, days=0):
        record_data = self.read_record(days=days)
        return record_data.get("activity", [])

    def read_summary(self, days=0):
        record_data = self.read_record(days=days)
        return record_data.get("summary", {})

