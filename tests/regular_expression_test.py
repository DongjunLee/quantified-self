# -*- coding: utf-8 -*-

import re
import unittest


class RegularExpressionTester(unittest.TestCase):
    def testRegExp1(self):
        string = "Test"
        matcher = re.compile(r"(.*)", re.I)
        result = matcher.match(string)
        self.assertEqual(result.groups(), ("Test",))

    def testRegExp2(self):
        string = "Give me money"

        matcher = re.compile("Give me (.*)", re.I)
        result = matcher.match(string)
        print(result.groups())
        self.assertEqual(result.groups(), ("money",))

    def testRegExp3(self):
        string = "stat star stan"

        matcher = re.compile("stat (.*) (.*)", re.I)
        result = matcher.match(string)
        print(result.groups())
        self.assertEqual(result.groups(), ("star", "stan"))

    def testAlarmManagerCreateCommand(self):
        string = "알람등록 텍스트 + 주기"

        matcher = re.compile("알람등록 (.*)", re.I)
        result = matcher.match(string)
        self.assertEqual(result.groups(), ("텍스트 + 주기",))

    def testAlarmManagerReadCommand(self):
        string = "알람보기"

        matcher = re.compile(r"알람보기", re.I)
        result = matcher.match(string)
        self.assertEqual(bool(result), True)
        self.assertEqual(result.groups(), ())

    def testAlarmManagerUpdateCommand(self):
        string = "알람변경 텍스트 + 주기"

        matcher = re.compile("알람변경 (.*)", re.I)
        result = matcher.match(string)
        self.assertEqual(result.groups(), ("텍스트 + 주기",))

    def testAlarmManagerDeleteCommand(self):
        string = "알람삭제 #1"

        matcher = re.compile("알람삭제 (.*)", re.I)
        result = matcher.match(string)
        self.assertEqual(result.groups(), ("#1",))
