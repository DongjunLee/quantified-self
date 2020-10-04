# -*- coding: utf-8 -*-

import calendar
import json
from pathlib import Path

import arrow
import boto3
import pandas as pd

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

    HABITS = [
        "bat",
        "blog",
        "diary",
        "exercise"
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

    def read_record_df_by_metrics(self):
        metrics = [
            {
                "name": "metric_v0",
                "start_date": "2017-01-30",
                "end_date": "2020-08-23",
            },
            {
                "name": "metric_v1",
                "start_date": "2020-08-24",
                "end_date": "2021-12-31",
            },
        ]

        metric_dfs = {}
        for m in metrics:
            records = self.read_records_by_date(m["start_date"], m["end_date"])
            metric_dfs[m["name"]] = {
                "daily_summary": self._make_daily_summary_df(records),
                "sleep_activity": self._make_sleep_activity_df(records),
                "task_activity": self._make_task_activity_df(records),
            }
        return metric_dfs

    def _make_daily_summary_df(self, records):
        datas = []
        for r in records:
            activity_data = r.get("activity", None)
            if activity_data is None:
                continue

            task_activity = activity_data.get("task", [])
            sleep_activity = activity_data.get("sleep", [])

            if len(task_activity) == 0 or len(sleep_activity) == 0:
                continue

            sleep_hour = None
            for s in sleep_activity:
                if s["is_main"]:
                    end_time = s["end_time"]
                    sleep_hour = (arrow.get(s["end_time"]) - arrow.get(s["start_time"])).seconds / 3600
                    break

            if sleep_hour is None:
                continue

            task_count = len(task_activity)
            task_hour = 0
            for t in task_activity:
                task_hour += (arrow.get(t["end_time"]) - arrow.get(t["start_time"])).seconds / 3600

            end_time = task_activity[0]["end_time"]

            summary_data = r.get("summary", {})
            data = {
                "sleep_hour": sleep_hour,
                "task_count": task_count,
                "task_hour": task_hour,
                "time": end_time,
                "attention_score": summary_data.get("attention", 0),
                "productive_score": summary_data.get("productive", 0),
                "happy_score": summary_data.get("happy", 0),
                "repeat_task_score": summary_data.get("repeat_task", 0),
                "sleep_score": summary_data.get("sleep", 0),
                "total_score": summary_data.get("total", 0),
            }
            datas.append(data)

        df = pd.DataFrame(datas)
        df["year"] = df["time"].apply(lambda x: str(arrow.get(x).year))
        df["month"] = df["time"].apply(lambda x: arrow.get(x).format("MM"))
        df["day"] = df["time"].apply(lambda x: arrow.get(x).format("DDD"))
        df = df.drop_duplicates(subset=["year", "day"])
        return df

    def _make_sleep_activity_df(self, records):
        datas = []
        for r in records:
            task_empty = False
            task_activity = r.get("activity", {}).get("task", [])
            task_activity = [t for t in task_activity if "score" in t]
            if len(task_activity) == 0:
                task_empty = True

            happy_empty = False
            happy_activity = r.get("activity", {}).get("happy", [])
            if len(happy_activity) == 0:
                happy_empty = True

            sleep_activity = r.get("activity", {}).get("sleep", [])

            end_time = None
            sleep_time = None
            for s in sleep_activity:
                if s["is_main"]:
                    end_time = s["end_time"]
                    sleep_time = (arrow.get(s["end_time"]) - arrow.get(s["start_time"])).seconds / 60
                    break

            attention_score = r.get("summary", {}).get("attention", None)
            happy_score = r.get("summary", {}).get("happy", None)

            if attention_score is None or happy_score is None or sleep_time is None:
                continue

            data = {
                "task_empty": task_empty,
                "happy_empty": happy_empty,
                "attention_score": attention_score,
                "happy_score": happy_score,
                "time": end_time,
                "sleep_time": sleep_time,
                "year": str(arrow.get(end_time).year),
            }
            datas.append(data)

        df = pd.DataFrame(datas)
        df["weekday"] = df["time"].apply(lambda x: calendar.day_name[arrow.get(x).isoweekday()-1])
        return df

    def _make_task_activity_df(self, records, PAD_MINUTES=30):
        datas = []
        for r in records:
            task_activity = r.get("activity", {}).get("task", [])
            happy_activity = r.get("activity", {}).get("happy", [])

            for h in happy_activity:
                happy_time = arrow.get(h["time"])

                for t in task_activity:
                    task_start_time = arrow.get(t["start_time"]).shift(minutes=-PAD_MINUTES)
                    task_end_time = arrow.get(t["end_time"]).shift(minutes=+PAD_MINUTES)

                    # TODO: change data
                    if t["project"] == "BeAwesomeToday":
                        t["project"] = "Review"
                    if t["project"] == "Deep Learning":
                        t["project"] = "Research"

                    if happy_time < task_start_time:
                        break
                    if task_start_time <= happy_time <= task_end_time:
                        t["happy_score"] = h["score"]

            datas += task_activity

        df = pd.DataFrame(datas)
        df["category"] = df["project"]
        df["attention_score"] = df["score"]

        df["date"] = df["end_time"].apply(lambda x: arrow.get(x).format("YYYY-MM-DD"))
        df["year"] = df["end_time"].apply(lambda x: str(arrow.get(x).year))
        df["month"] = df["end_time"].apply(lambda x: arrow.get(x).format("MM"))
        df["start_hour"] = df["start_time"].apply(lambda x: arrow.get(x).hour + arrow.get(x).minute / 60)

        df["working_hours"] = df.apply(lambda x: (arrow.get(x.end_time) - arrow.get(x.start_time)).seconds / 3600, axis=1)
        df["working_minutes"] = df.apply(lambda x: int((arrow.get(x.end_time) - arrow.get(x.start_time)).seconds / 60), axis=1)
        df["working_hours_text"] = df["working_minutes"].apply(lambda x: f"{x//60}:{x%60:02d}")
        return df

    def read_records_by_date(self, start_date, end_date):
        record_path = Path(self.record_path)

        records = []
        for f in record_path.iterdir():
            if f.suffix != ".json":
                continue
            if start_date <= f.stem <= end_date:
                records.append(self.read_file(f))
        return records

    def read_acitivity(self, days=0):
        record_data = self.read_record(days=days)
        return record_data.get("activity", [])

    def read_summary(self, days=0):
        record_data = self.read_record(days=days)
        return record_data.get("summary", {})

    def read_habit(self, days=0):
        summary_data = self.read_summary(days=days)
        if "habit" in summary_data:
            return summary_data["habit"]
        else:
            return summary_data

    def read_habit_results(self, days=0):
        habit_data = self.read_habit(days=days)

        habit_results = []
        for habit in self.HABITS:
            if (habit in habit_data and habit_data[habit]) or \
                (f"do_{habit}" in habit_data and habit_data[f"do_{habit}"]):
                habit_result = "O"
            else:
                habit_result = "X"

            habit_results.append(habit_result)
        return habit_results

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
        task_reports = self._initialize_task_reports(base_dates, group_by=group_by)

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

    def _initialize_task_reports(self, base_dates, group_by=TaskGroup.TIME):
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
        if category == "Empty":
            print(task_data)
            return  # Skip

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
            if category not in colors and "color" in task_data:
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


