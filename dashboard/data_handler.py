# -*- coding: utf-8 -*-

import arrow
import boto3
import json

from date_unit import DateUnit, TaskGroup


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

    def make_task_reports(
        self,
        start_date,
        end_date,
        colors=None,
        date_unit=DateUnit.DAILY,
        group_by=TaskGroup.TIME,
        return_base_dates=False
    ):
        start_date = arrow.get(start_date)
        end_date = arrow.get(end_date)

        base_dates = self._make_base_dates(start_date, end_date, date_unit=date_unit)
        task_reports = self._initialize_tass_reports(base_dates, group_by=group_by)

        if date_unit == DateUnit.DAILY:
            for daily_index, r in enumerate(arrow.Arrow.range("day", start_date, end_date)):
                offset_day = (arrow.now() - r).days
                record_data = self.read_record(days=-offset_day)

                activity_data = record_data.get("activity", {})
                task_datas = activity_data.get("task", [])
                for task_data in task_datas:
                    self._mapping_task_data_to_reports(
                        task_data,
                        daily_index,
                        task_reports,
                        colors=colors,
                        group_by=group_by,
                    )

        elif date_unit == DateUnit.WEEKLY:
            weekly_index = 0
            for r in arrow.Arrow.range("day", start_date, end_date):
                offset_day = (arrow.now() - r).days
                record_data = self.read_record(days=-offset_day)

                for weekly_index, base_date in enumerate(base_dates):
                    days_diff = (base_date.date() - r.date()).days
                    if days_diff < 7 and days_diff >= 0:
                        break

                activity_data = record_data.get("activity", {})
                task_datas = activity_data.get("task", [])
                for task_data in task_datas:
                    self._mapping_task_data_to_reports(
                        task_data,
                        weekly_index,
                        task_reports,
                        colors=colors,
                        group_by=group_by,
                    )

        if return_base_dates is True:
            base_dates = [d.format("YYYY-MM-DD HH:mm:ss") for d in base_dates]
            return base_dates, task_reports
        return task_reports

    def _make_base_dates(self, start_date, end_date, date_unit=DateUnit.DAILY):
        if date_unit == DateUnit.DAILY:
            base_dates = [date.replace(hour=0, minute=0) for date in arrow.Arrow.range("day", start_date, end_date)]
        elif date_unit == DateUnit.WEEKLY:
            base_dates = self.get_weekly_base_of_range(start_date, end_date, weekday_value=self.BASE_WEEKDAY)
        else:
            raise ValueError("Invalid DateUnit")
        return base_dates

    def _initialize_tass_reports(self, base_dates, group_by=TaskGroup.TIME):
        task_reports = {}
        for c in self.TASK_CATEGORIES:
            if group_by == TaskGroup.TIME:
                task_reports[c] = [0] * len(base_dates)
            elif group_by == TaskGroup.TASK_NAME:
                task_reports[c] = []
                for i in range(len(base_dates)):
                    task_reports[c].append({})  # independent dict
        return task_reports

    def _mapping_task_data_to_reports(self, task_data, index, task_reports, colors=None, group_by=TaskGroup.TIME):
        category = task_data["project"]

        duration = (arrow.get(task_data["end_time"]) - arrow.get(task_data["start_time"])).seconds
        duration_hours = round(duration / 60 / 60, 1)

        if group_by == TaskGroup.TIME:
            task_reports[category][index] += duration_hours
        elif group_by == TaskGroup.TASK_NAME:
            task_name = task_data["description"].split(" - ")[1]  # FIXED
            if task_name in task_reports[category][index]:
                task_reports[category][index][task_name] += duration_hours
            else:
                task_reports[category][index][task_name] = duration_hours

        # Color (For Task Stacked Bar)
        if colors is not None:
            if category not in colors:
                colors[category] = task_data["color"]

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


