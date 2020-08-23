# -*- coding: utf-8 -*-
import collections
import os
import re

import arrow
import boto3
import json
import requests

from hbconfig import Config

from kino.utils.arrow import ArrowUtil


class DataHandler(object):

    def __init__(self):
        self.data_path = "data/"
        self.record_path = "record/"
        self.log_data_path = "log/data/"

        self.s3_client = None
        if Config.db.record_upload_to_s3:
            self.s3_client = boto3.client(
                's3',
                aws_access_key_id=Config.db.s3.ACCESS_KEY,
                aws_secret_access_key=Config.db.s3.SECRET_KEY
            )

    def read_file(self, fname):
        text = self.read_text(fname)
        if text == "":
            return {}
        else:
            return json.loads(text)

    def read_text(self, fname, fpath=None):
        if fpath is None:
            fpath = self.data_path

        path = os.path.join(fpath + fname)
        try:
            with open(path, "rb") as infile:
                return infile.read().decode("utf-8")
        except BaseException:
            return ""

    def write_file(self, fname, data):
        path = os.path.join(self.data_path + fname)
        with open(path, "w", encoding="utf-8") as outfile:
            json.dump(data, outfile, indent=4)

    def read_json_then_add_data(self, fname, category, input_data):
        total_data = self.read_file(fname)
        category_data = total_data.get(category, {})

        if category_data == {}:
            total_data[category] = category_data
            c_index = 1
        else:
            c_index = category_data["index"] + 1
        category_data["index"] = c_index
        c_index = "#" + str(c_index)
        category_data[c_index] = input_data

        self.write_file(fname, total_data)

        return total_data, c_index

    def read_json_then_edit_data(self, fname, category, c_index, input_data):
        total_data = self.read_file(fname)
        category_data = total_data.get(category, {})

        if c_index not in category_data:
            return "not exist"

        category_data[c_index] = input_data
        self.write_file(fname, total_data)

        return "success"

    def read_json_then_delete(self, fname, category, index):
        total_data = self.read_file(fname)
        category_data = total_data.get(category, {})
        category_data.pop(index, None)
        self.write_file(fname, total_data)

    def get_current_data(self, fname, category):
        total_data = self.read_file(fname)
        category_data = total_data[category]
        c_index = "#" + str(category_data["index"])
        current_category_data = category_data[c_index]
        return c_index, current_category_data

    def read_record(self, days=0, date_string=None):
        date = arrow.now().shift(days=int(days))
        if date_string is not None:
            date = arrow.get(date_string)
        fname = self.record_path + date.format("YYYY-MM-DD") + ".json"
        return self.read_file(fname)

    def write_record(self, data, days=0):
        date = arrow.now().shift(days=int(days))
        fname = self.record_path + date.format("YYYY-MM-DD") + ".json"
        self.write_file(fname, data)

        if Config.db.record_upload_to_s3:
            file_path = os.path.join(self.data_path, fname)
            bucket_name = Config.db.s3.RECORD_BUCKET_NAME

            year = date.format("YYYY")
            basename = date.format("YYYY-MM-DD") + ".json"
            object_key = f"{year}/{basename}"

            self.s3_client.upload_file(file_path, bucket_name, object_key)

    def edit_record(self, data, days=0):
        def update(d, u):
            """ dictionary update recursively  """
            for k, v in u.items():
                if isinstance(v, collections.abc.Mapping):
                    d[k] = update(d.get(k, {}), v)
                else:
                    d[k] = v
            return d

        record = self.read_record(days=days)
        if isinstance(data, tuple):
            record[data[0]] = data[1]
        elif isinstance(data, dict):
            update(record, data)

        self.write_record(record, days=days)

    def edit_record_with_category(self, category, data, days=0):
        record = self.read_record(days=days)
        category_data = record.get(category, {})
        category_data[data[0]] = data[1]
        self.edit_record((category, category_data), days=days)

    def read_acitivity(self, days=0):
        record_data = self.read_record(days=days)
        return record_data.get("activity", [])

    def edit_activity(self, category, data, days=0):
        record = self.read_record(days=days)
        activity_data = record.get("activity", {})
        if type(data) == list:
            activity_data[category] = data
        elif type(data) == dict:
            if category in activity_data:
                activity_data[category].append(data)
            else:
                activity_data[category] = [data]
        else:
            raise ValueError("only 'list' and 'dict' type is availabile.")

        self.edit_record(("activity", activity_data), days=days)

    def edit_attention(self, category, data, days=0):
        record = self.read_record(days=days)
        activity_data = record.get("activity", {})

        assert category in activity_data

        latest_data = activity_data[category][-1]
        task_end_time = arrow.get(latest_data["end_time"])
        current_time = data["time"]

        if ArrowUtil.get_curr_time_diff(task_end_time, current_time) < 40:
            latest_data["score"] = data["score"]
        else:
            pass

        self.edit_record(("activity", activity_data), days=days)

    def read_summary(self, days=0):
        record_data = self.read_record(days=days)
        return record_data.get("summary", {})

    def edit_summary(self, data, days=0):
        record = self.read_record(days=days)
        summary_data = record.get("summary", {})
        summary_data.update(data)
        self.edit_record(("summary", summary_data), days=days)

    def read_habit(self, days=0):
        summary_data = self.read_summary(days=days)
        if "habit" in summary_data:
            return summary_data["habit"]
        else:
            return summary_data

    def edit_habit(self, data, days=0):
        habit_data = self.read_habit(days=days)
        habit_data.update(data)
        self.edit_summary({"habit": habit_data}, days=days)

    def read_cache(self, fname="cache.json"):
        return self.read_file(fname)

    def edit_cache(self, data, fname="cache.json"):
        cache = self.read_cache(fname=fname)
        cache[data[0]] = data[1]
        self.write_file(fname, cache)

    def read_template(self):
        templates = {}

        template_dir = "template/"
        for f in os.listdir(self.data_path + template_dir):
            if f.endswith(".json"):
                lang_code = f.split(".")[0]
                templates[lang_code] = self.read_file(template_dir + f)
        return templates

    def read_feeds(self):
        awesome_feeds_url = Config.profile.feed.get(
            "AWESOME_FEEDS_URL",
            "https://raw.githubusercontent.com/DongjunLee/awesome-feeds/master/README.md",
        )
        raw_awesome_feeds = requests.get(awesome_feeds_url).text

        feeds = {"Github": [("Activity", Config.profile.feed.get("GITHUB", ""), False)]}
        curr_category = None
        for line in raw_awesome_feeds.splitlines():
            if line.startswith("##"):
                category = line.replace("## ", "")
                feeds[category] = []
                curr_category = category
            elif line.startswith("- "):
                feed_name = re.findall("\[.+\]", line)[0][1:-1]
                line = line.replace(" ", "")
                feed_link = line[line.index("):") + len("):") :]
                save_pocket = False
                if "**" in feed_name:
                    save_pocket = True
                    feed_name = feed_name.replace("**", "")

                feeds[curr_category].append((feed_name, feed_link, save_pocket))
        return feeds

    def read_log_data(self, fname):
        return self.read_text(fname, fpath=self.log_data_path)

    def read_metric(self):
        metric_path = Config.metric.file_path
        metric = self.read_file(metric_path)
        if metric == {}:
            raise ValueError("Error. check metric_path")

        Metric = collections.namedtuple("Metric", "meta total attention happy habit productive sleep repeat_task holiday_policy")
        return Metric(
            meta=metric["meta"],
            total=metric["total"],
            attention=metric["detail"]["attention"],
            happy=metric["detail"]["happy"],
            habit=metric["detail"]["habit"],
            productive=metric["detail"]["productive"],
            sleep=metric["detail"]["sleep"],
            repeat_task=metric["detail"]["repeat_task"],
            holiday_policy=metric["holiday_policy"],
        )
