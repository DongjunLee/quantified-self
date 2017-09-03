# -*- coding: utf-8 -*-

import arrow
import json
import os
import re
import requests


class DataHandler(object):

    def __init__(self):
        self.data_path = "data/"
        self.record_path = "record/"

    def read_file(self, fname):
        text = self.read_text(fname)
        if text == "":
            return {}
        else:
            return json.loads(text)

    def read_text(self, fname):
        path = os.path.join(self.data_path + fname)
        try:
            with open(path, 'r') as infile:
                return infile.read()
        except BaseException:
            return ""

    def write_file(self, fname, data):
        path = os.path.join(self.data_path + fname)
        with open(path, 'w') as outfile:
            json.dump(data, outfile)

    def read_json_then_add_data(self, fname, category, input_data):
        total_data = self.read_file(fname)
        category_data = total_data.get(category, {})

        if category_data == {}:
            total_data[category] = category_data
            c_index = 1
        else:
            c_index = category_data['index'] + 1
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
        c_index = "#" + str(category_data['index'])
        current_category_data = category_data[c_index]
        return c_index, current_category_data

    def read_record(self, days=0, date_string=None):
        date = arrow.now().replace(days=int(days))
        if date_string is not None:
            date = arrow.get(date_string)
        fname = self.record_path + date.format('YYYY-MM-DD') + ".json"
        return self.read_file(fname)

    def write_record(self, data, days=0):
        date = arrow.now().replace(days=int(days))
        fname = self.record_path + date.format('YYYY-MM-DD') + ".json"
        self.write_file(fname, data)

    def edit_record(self, data, days=0):
        record = self.read_record(days=days)
        if isinstance(data, tuple):
            record[data[0]] = data[1]
        elif isinstance(data, dict):
            for k, v in data.items():
                record[k] = v
        self.write_record(record, days=days)

    def edit_record_with_category(self, category, data, days=0):
        record = self.read_record(days=days)
        category_data = record.get(category, {})
        category_data[data[0]] = data[1]
        self.edit_record((category, category_data), days=days)

    def read_cache(self):
        fname = "cache.json"
        return self.read_file(fname)

    def edit_cache(self, data):
        fname = "cache.json"
        cache = self.read_cache()
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
        awesome_feeds_url = 'https://raw.githubusercontent.com/DongjunLee/awesome-feeds/master/README.md'
        raw_awesome_feeds = requests.get(awesome_feeds_url).text

        feeds = {}
        curr_category = None
        for line in raw_awesome_feeds.splitlines():
            if line.startswith("##"):
                category = line.replace("## ", "")
                feeds[category] = []
                curr_category = category
            elif line.startswith("- "):
                feed_name = re.findall("\[.+\]", line)[0][1:-1]
                line = line.replace(" ", "")
                feed_link = line[line.index("):") + len("):"):]

                feeds[curr_category].append((feed_name, feed_link))
        return feeds
