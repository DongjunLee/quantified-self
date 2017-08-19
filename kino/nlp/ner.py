# -*- coding: utf-8 -*-

import re

from ..utils.data_handler import DataHandler


class NamedEntitiyRecognizer(object):
    class __NER:

        SPLIT_PATTERN = " |&| "

        def __init__(self):
            self.data_handler = DataHandler()

            self.ner = self.data_handler.read_file("ner.json")
            self.kino = self.ner['kino']
            self.schedule = self.ner['schedule']
            self.skills = self.data_handler.read_file("skills.json")
            self.params = self.ner['params']

        def parse(self, item, text, get_all=False):

            ner_list = []
            for item_name, item_pattern in item.items():
                item_pattern_type = type(item_pattern)

                # DICT => recursive
                if isinstance({}, item_pattern_type):
                    sub_ner = self.parse(item_pattern, text)
                    if sub_ner:
                        ner_list.append((item_name, sub_ner))

                # LIST => str type -> match, list type -> 'AND' match
                elif isinstance([], item_pattern_type):
                    for p in item_pattern:
                        p_type = type(p)
                        if isinstance([], p_type):
                            ps = p
                            result = all([p in text for p in ps])
                        else:
                            result = p in text

                        if result:
                            if get_all:
                                ner_list.append(item_name)
                            else:
                                return item_name

                # STR => str -> regex
                elif isinstance("", item_pattern_type):
                    if self.SPLIT_PATTERN in text:
                        text = text[text.index(self.SPLIT_PATTERN) + len(self.SPLIT_PATTERN):]

                    result = re.findall(item_pattern, text)
                    if len(result) != 0:
                        if get_all:
                            ner_list += result
                        else:
                            return result[0]

            if len(ner_list) == 0:
                return None
            else:
                return ner_list

    instance = None

    def __init__(self):
        if not NamedEntitiyRecognizer.instance:
            NamedEntitiyRecognizer.instance = NamedEntitiyRecognizer.__NER()

    def __getattr__(self, name):
        return getattr(self.instance, name)
