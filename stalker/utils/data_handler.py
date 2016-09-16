# -*- coding: utf-8 -*-

import json

class DataHandler(object):

    def __init__(self):
        pass

    def read_file(self, fname):
        with open(fname, 'r') as infile:
            return json.loads(infile.read())

    def write_file(self, fname, data):
        with open(fname, 'w') as outfile:
            json.dump(data, outfile)
