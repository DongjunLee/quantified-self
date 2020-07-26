# -*- coding: utf-8 -*-

import arrow
import boto3
import json

from date_unit import DateUnit


class DataHandler:

    TASK_CATEGORIES = [
        "Article",
        "Blog",
        "Book",
        "Develop",
        "Exercise",
        "Hobby",
        "Management",
        "Meeting",
        "MOOC",
        "Planning",
        "Research",
        "Review",
        "Seminar",
        "Think",
    ]

    BASE_WEEKDAY = 6  # Sunday

    GOOD_COLOR = "palegreen"
    BAD_COLOR = "lightsalmon"

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

    def read_kpi(self):
        return self.read_file("kpi.json")

    def make_task_reports(self, start_date, end_date, colors=None, date_unit=DateUnit.DAILY, return_base_dates=False):
        start_date = arrow.get(start_date)
        end_date = arrow.get(end_date)

        task_reports = {}

        if date_unit == DateUnit.DAILY:
            base_dates = [date.replace(hour=0, minute=0) for date in arrow.Arrow.range("day", start_date, end_date)]

            for c in self.TASK_CATEGORIES:
                task_reports[c] = [0] * len(base_dates)

            for daily_index, r in enumerate(arrow.Arrow.range("day", start_date, end_date)):
                offset_day = (arrow.now() - r).days
                record_data = self.read_record(days=-offset_day)

                activity_data = record_data.get("activity", {})
                task_data = activity_data.get("task", [])
                for t in task_data:
                    project = t["project"]

                    duration = (arrow.get(t["end_time"]) - arrow.get(t["start_time"])).seconds
                    duration_hours = round(duration / 60 / 60, 1)

                    task_reports[project][daily_index] += duration_hours

                    # Color (For Task Stacked Bar)
                    if colors is not None:
                        if project not in colors:
                            colors[project] = t["color"]

        elif date_unit == DateUnit.WEEKLY:
            base_dates = self.get_weekly_base_of_range(start_date, end_date, weekday_value=self.BASE_WEEKDAY)

            for c in self.TASK_CATEGORIES:
                task_reports[c] = [0] * len(base_dates)

            weekly_index = 0
            for r in arrow.Arrow.range("day", start_date, end_date):
                offset_day = (arrow.now() - r).days
                record_data = self.read_record(days=-offset_day)

                for weekly_index, base_date in enumerate(base_dates):
                    days_diff = (base_date.date() - r.date()).days
                    if days_diff < 7 and days_diff >= 0:
                        break

                activity_data = record_data.get("activity", {})
                task_data = activity_data.get("task", [])
                for t in task_data:
                    project = t["project"]

                    duration = (arrow.get(t["end_time"]) - arrow.get(t["start_time"])).seconds
                    duration_hours = round(duration / 60 / 60, 1)

                    task_reports[project][weekly_index] += duration_hours

                    # Color (For Task Stacked Bar)
                    if colors is not None:
                        if project not in colors:
                            colors[project] = t["color"]

        if return_base_dates is True:
            base_dates = [d.format("YYYY-MM-DD HH:mm:ss") for d in base_dates]
            return base_dates, task_reports
        return task_reports

    def get_daily_base_of_range(self, start_date, end_date):
        base_dates = []
        for r in arrow.Arrow.range("day", start_date, end_date):
            base_dates.append(r)
        return base_dates

    def get_weekly_base_of_range(self, start_date, end_date, weekday_value=0):
        # if start_date.weekday() != weekday_value:
        # start_date = start_date.shift(days=-(start_date.weekday() - weekday_value))
        if end_date.weekday() != weekday_value:
            end_date = end_date.shift(days=+(abs(end_date.weekday() - weekday_value)))

        base_dates = []
        for r in arrow.Arrow.range("day", start_date, end_date):
            if r.weekday() == weekday_value:
                base_dates.append(r)
        return base_dates


