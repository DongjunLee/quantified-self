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
