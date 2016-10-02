# -*- coding: utf-8 -*-

import json

class DataHandler(object):

    def __init__(self):
        self.data_path = "../data/"

    def read_file(self, fname):
        try:
            with open(self.data_path + fname, 'r') as infile:
                return json.loads(infile.read())
        except:
            return {}

    def write_file(self, fname, data):
        with open(self.data_path + fname, 'w') as outfile:
            json.dump(data, outfile)

    def read_json_then_add_data(self, fname, category, input_data):
        total_data = self.read_file(fname)
        category_data = total_data.get(category, {})

        if category_data == {}:
            total_data[category]= category_data
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


