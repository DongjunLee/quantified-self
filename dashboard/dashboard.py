import arrow

from data_handler import DataHandler
from date_unit import DateUnit


data_handler = DataHandler()

start_date = arrow.now().shift(days=-14)
end_date = arrow.now()
this_week_task_reports = data_handler.make_task_reports(start_date, end_date, date_unit=DateUnit.WEEKLY)



def get_background_color(value, thresholds=[]):
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

    remain_hour = 24 - task_hour - sleep_hour

    today_summary = today_record_data.get("summary", {})

    exercise = "X"
    if "do_exercise" in today_summary and today_summary["do_exercise"]:
        exercise= "O"

    diary = "X"
    if "do_diary" in today_summary and today_summary["do_diary"]:
        diary= "O"

    bat = "X"
    if "do_bat" in today_summary and today_summary["do_bat"]:
        bat= "O"

    results = [
        get_background_color(task_hour, daily_kpi["task_hour"]),
        round(task_hour, 1),
        get_background_color(sleep_hour, daily_kpi["sleep_hour"]),
        round(sleep_hour, 1),
        get_background_color(remain_hour),
        round(remain_hour, 1),
        get_background_color(exercise, daily_kpi["exercise"]),
        exercise,
        get_background_color(diary, daily_kpi["diary"]),
        diary,
        get_background_color(bat, daily_kpi["bat"]),
        bat
    ]
    return results


def _update_weekly(weekly_kpi):
    end_date = arrow.now()
    start_date = end_date.shift(days=-end_date.weekday())

    WEEKDAY_SUNDAY = 6
    sunday_dates = data_handler.get_weekly_base_of_range(start_date, end_date, weekday_value=WEEKDAY_SUNDAY)

    bat_count = 0
    diary_count = 0
    exercise_count = 0

    weekly_index = 0
    for r in arrow.Arrow.range("day", start_date, end_date):
        offset_day = (arrow.now() - r).days
        record_data = data_handler.read_record(days=-offset_day)

        summary_data = record_data.get("summary", None)
        if summary_data is None:
            pass
        else:
            if "do_bat" in summary_data and summary_data["do_bat"] is True:
                bat_count += 1
            if "do_diary" in summary_data and summary_data["do_diary"] is True:
                diary_count += 1
            if "do_exercise" in summary_data and summary_data["do_exercise"] is True:
                exercise_count += 1

        for weekly_index, base_date in enumerate(sunday_dates):
            days_diff = (base_date - r).days
            if days_diff < 7 and days_diff >= 0:
                break

    results = [
        get_background_color(bat_count, weekly_kpi["bat_count"]),
        bat_count,
        get_background_color(diary_count, weekly_kpi["diary_count"]),
        diary_count,
        get_background_color(exercise_count, weekly_kpi["exercise_count"]),
        exercise_count,
    ]
    return results


def _update_weekly_task_category(weekly_kpi):
    results = []
    total_hour = 0
    for task_category in data_handler.TASK_CATEGORIES:
        if task_category == "Empty":
            continue

        task_hour = round(this_week_task_reports[task_category][-1], 1)
        total_hour += task_hour

        results.append(get_background_color(task_hour, weekly_kpi.get(task_category.lower(), [])))
        results.append(task_hour)

    total_hour_result = [
        get_background_color(total_hour, weekly_kpi["task_hour"]),
        round(total_hour, 1)
    ]
    results = total_hour_result + results
    return results
