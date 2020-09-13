import arrow

import dash_html_components as html

from data_handler import DataHandler
from date_unit import DateUnit, TaskGroup


data_handler = DataHandler()

start_date = arrow.now().shift(days=-14)
end_date = arrow.now()

this_week_time_task_reports = data_handler.make_task_reports(
    start_date,
    end_date,
    date_unit=DateUnit.WEEKLY,
    group_by=TaskGroup.TIME,
)
this_week_task_name_task_reports = data_handler.make_task_reports(
    start_date,
    end_date,
    date_unit=DateUnit.WEEKLY,
    group_by=TaskGroup.TASK_NAME,
)


def get_background_color(value, thresholds=[]):
    """ Based on KPI """
    background_color = "white"
    if value is None or len(thresholds) == 0:
        return {"background-color": background_color}

    if type(value) == int or type(value) == float:
        bad_threshold, good_threshold = thresholds
        if value >= good_threshold:
            background_color = data_handler.GOOD_COLOR
        elif value < bad_threshold:
            background_color = data_handler.BAD_COLOR

    if type(value) == str:
        bad_threshold, good_threshold = thresholds
        if value == good_threshold:
            background_color = data_handler.GOOD_COLOR
        elif value == bad_threshold:
            background_color = data_handler.BAD_COLOR

    return {"background-color": background_color}


def _update_daily(daily_kpi):
    today_record_data = data_handler.read_record(redownload=True)
    activity_data = today_record_data.get("activity", {})

    # Task & Sleep
    task_hour = 0
    today_tasks = activity_data.get("task", [])
    for t in today_tasks:
        duration = (arrow.get(t["end_time"]) - arrow.get(t["start_time"])).seconds
        duration_hours = duration / 60 / 60

        task_hour += duration_hours

    sleep_hour = 0
    today_sleep = activity_data.get("sleep", [])
    for s in today_sleep:
        if s["is_main"] is True:
            start_time = arrow.get(s["start_time"])
            end_time = arrow.get(s["end_time"])

            sleep_hour = (end_time - start_time).seconds
            sleep_hour = sleep_hour / 60 / 60

    results = [
        get_background_color(task_hour, daily_kpi["task_hour"]),
        round(task_hour, 1),
        get_background_color(sleep_hour, daily_kpi["sleep_hour"]),
        round(sleep_hour, 1),
    ]

    # Habits
    habit_results = data_handler.read_habit_results()
    for habit, result in zip(data_handler.HABITS, habit_results):
        results += [
            get_background_color(habit, daily_kpi[habit]),
            result
        ]
    return results


def _update_weekly(weekly_kpi):
    end_date = arrow.now()
    start_date = end_date.shift(days=-end_date.weekday())

    WEEKDAY_SUNDAY = 6
    sunday_dates = data_handler.get_weekly_base_of_range(start_date, end_date, weekday_value=WEEKDAY_SUNDAY)

    weekly_habit_results = []
    weekly_index = 0
    for r in arrow.Arrow.range("day", start_date, end_date):
        offset_day = (arrow.now() - r).days
        weekly_habit_results.append(data_handler.read_habit_results(days=-offset_day))

        for weekly_index, base_date in enumerate(sunday_dates):
            days_diff = (base_date - r).days
            if days_diff < 7 and days_diff >= 0:
                break

    weekly_habit_counts = {}
    for habit in data_handler.HABITS:
        weekly_habit_counts[habit] = 0

    for habit_results in weekly_habit_results:
        for i in range(len(data_handler.HABITS)):
            if habit_results[i] == "O":
                habit = data_handler.HABITS[i]
                weekly_habit_counts[habit] += 1

    results = []
    for habit, habit_count in weekly_habit_counts.items():
        results += [
            get_background_color(habit_count, weekly_kpi[f"{habit}_count"]),
            habit_count,
        ]
    return results


def _update_weekly_task_category(weekly_kpi):
    results = []
    total_hour = 0
    for task_category in data_handler.TASK_CATEGORIES:
        if task_category == "Empty":
            continue

        task_hour = round(this_week_time_task_reports[task_category][-1], 1)
        total_hour += task_hour

        task_html = html.Div([
            html.Span(task_hour),
            html.Hr(),
        ])

        task_list = html.Ul([], style={"text-align": "left"})
        for task_name, each_task_hour in sorted(
            this_week_task_name_task_reports[task_category][-1].items(),
            key=lambda x: x[1],
            reverse=True,
        ):
            task_list.children.append(html.Li(f"{task_name} : {round(each_task_hour, 1)}"))
        task_html.children.append(task_list)

        results.append(get_background_color(task_hour, weekly_kpi.get(task_category.lower(), [])))
        results.append(task_html)

    total_hour_result = [
        get_background_color(total_hour, weekly_kpi["task_hour"]),
        round(total_hour, 1)
    ]
    results = total_hour_result + results
    return results
