
import arrow
import calendar
import copy
import datetime
from dateutil import parser
import math
import random

import plotly.express as px
import plotly.figure_factory as ff
import plotly.graph_objs as go
from plotly.subplots import make_subplots

from data_handler import DataHandler
from date_unit import DateUnit


data_handler = DataHandler()


def _make_daily_schedule_fig(date):

    timedelta = arrow.now() - arrow.get(date, tzinfo="Asia/Seoul")
    days_diff = timedelta.days

    if days_diff < 0:
        pass  # Can't handle future!"
    elif days_diff == 0:
        record_data = data_handler.read_record(redownload=True)
    else:
        record_data = data_handler.read_record(days=-days_diff)

    activity_data = record_data.get("activity", {})
    task_data = activity_data.get("task", [])

    toggl_projects = [data["project"] for data in task_data]
    colors = {"Empty": "#DEDEDE"}
    for data in task_data:
        colors[data["project"]] = data["color"]

    base_date = date
    tomorrow_base_date = arrow.get(base_date).shift(days=+1).format("YYYY-MM-DD")

    DUMMY_RESOURCE = "Empty"
    df = [  # Labeling scores
        dict(Task=5, Start=base_date, Finish=base_date, Resource=DUMMY_RESOURCE),
        dict(Task=4, Start=base_date, Finish=base_date, Resource=DUMMY_RESOURCE),
        dict(Task=3, Start=base_date, Finish=base_date, Resource=DUMMY_RESOURCE),
        dict(Task=2, Start=base_date, Finish=base_date, Resource=DUMMY_RESOURCE),
        dict(Task=1, Start=base_date, Finish=base_date, Resource=DUMMY_RESOURCE),
    ]

    # Labeling projects
    for project in toggl_projects:
        df.append(
            dict(
                Task=1,
                Start=tomorrow_base_date,
                Finish=tomorrow_base_date,
                Resource=project,
            )
        )

    for data in task_data:
        task = {
            "Task": data.get("score", 3),
            "Start": arrow.get(data["start_time"]).format("YYYY-MM-DD HH:mm"),
            "Finish": arrow.get(data["end_time"]).format("YYYY-MM-DD HH:mm"),
            "Resource": data["project"],
            "Description": data["description"],
        }
        df.append(task)

    # fig = px.timeline(
        # df,
        # x_start="Start",
        # x_end="End",
        # y="Attention",
        # color="Task",
        # color_discrete_map=colors,
        # hover_data={
            # "Start": "|%Y-%m-%dT%H:%M",
            # "End": True,
            # "Attention": True,
            # "Task": True,
            # "Description": True,
        # },
        # title="Daily Schedule",
        # width=1000,
        # height=500,
    # )

    fig = ff.create_gantt(
        df,
        colors=colors,
        index_col="Resource",
        title="Daily Schedule",
        group_tasks=True,
        show_colorbar=True,
        bar_width=0.3,
        showgrid_x=True,
        showgrid_y=True,
        width=800,
        height=500,
    )

    happy_data = activity_data.get("happy", [])

    if len(happy_data) > 0:
        xs = [arrow.get(d["time"]).format("YYYY-MM-DD HH:mm:ss") for d in happy_data]
        ys = [d["score"] - 1 for d in happy_data]

        scatter_trace = dict(
            type="scatter",
            mode="markers",
            marker=dict(size=10, color="#439C59", line=dict(width=2)),
            name="Happy",
            x=xs,
            y=ys,
        )
        fig.add_trace(scatter_trace)

    # Annotations
    up_index, down_index = -1, -1

    up_ays = [i for i in range(30, 200, 20)]
    down_ays = [-i for i in up_ays]

    annotations = []
    for d in fig["data"]:
        if d["text"] is None:
            continue

        data_count = len(d["x"])
        for i in range(0, data_count, 2):

            text = d["text"][i]
            if text is None:
                continue

            start_date = d["x"][i]
            end_date = d["x"][i + 1]

            start_score = d["y"][i]
            end_score = d["y"][i + 1]

            if start_date == end_date or start_score != end_score:
                continue

            description = d["text"][i]
            project_names = list(colors.keys())

            project_name = "Empty"
            for p_name in project_names:
                if description.startswith(p_name):
                    project_name = p_name
                    break

            if type(start_date) != datetime.datetime:
                start_date = parser.parse(start_date)
            if type(end_date) != datetime.datetime:
                end_date = parser.parse(end_date)

            if start_score > 2:  # large than 3
                ays = down_ays
                down_index += 1
                index = down_index
            else:
                ays = up_ays
                up_index += 1
                index = up_index

            ay = ays[index % len(ays)]

            annotations.append(
                go.layout.Annotation(
                    x=start_date + (end_date - start_date) / 2,
                    y=start_score,
                    xref="x",
                    yref="y",
                    text=description,
                    font=dict(family="Courier New, monospace", size=12, color="#fff"),
                    bgcolor=colors.get(project_name, "#DEDEDE"),
                    bordercolor="#666",
                    borderpad=2,
                    arrowhead=7,
                    ax=0,
                    ay=ay,
                    opacity=0.7,
                )
            )

    fig.update_layout(annotations=annotations)

    return fig


def _make_task_stacked_bar_fig(start_date, end_date, date_unit=DateUnit.DAILY):
    colors = {"Empty": "#DEDEDE"}
    base_dates, task_reports = data_handler.make_task_reports(
        start_date,
        end_date,
        colors=colors,
        date_unit=date_unit,
        return_base_dates=True,
    )

    data = []
    for category, task_report in task_reports.items():

        differ_with_last_date = [f"{task_report[0]} (0)"]
        for i in range(1, len(task_report)):
            last_week_task_time = task_report[i - 1]
            task_time = task_report[i]
            differ_time = round(task_time - last_week_task_time, 2)
            plus_and_minus = "+"
            if differ_time < 0:
                plus_and_minus = ""

            differ_with_last_date.append(
                f"{round(task_time, 2)} ({plus_and_minus}{differ_time})"
            )

        data.append(
            go.Bar(
                x=base_dates,
                y=task_report,
                name=category,
                marker=dict(
                    color=colors.get(category, "#DEDEDE"),
                    line=dict(color="#222", width=1),
                ),
                hovertext=differ_with_last_date,
                opacity=0.8,
            )
        )

    layout = go.Layout(
        autosize=True,
        barmode="stack",
        title=f"{date_unit.value} Task Report (Stack Bar)",
        xaxis={
            "tickformat":'%m-%d %a'
        }
    )

    fig = go.Figure(data=data, layout=layout)
    return fig


def _make_pie_chart_fig(start_date, end_date):
    start_date = arrow.get(start_date).replace(tzinfo='Asia/Seoul')
    end_date = arrow.get(end_date).replace(tzinfo='Asia/Seoul')

    categories = copy.deepcopy(data_handler.TASK_CATEGORIES)
    categories.append("Empty")

    task_reports = {}

    colors = {"Empty": "#DEDEDE"}

    sunday_dates = data_handler.get_weekly_base_of_range(start_date, end_date, weekday_value=data_handler.BASE_WEEKDAY)

    for c in categories:
        task_reports[c] = [0] * len(sunday_dates)

    weekly_index = 0
    for r in arrow.Arrow.range("day", start_date, end_date):
        offset_day = (arrow.now() - r).days
        record_data = data_handler.read_record(days=-offset_day)

        for weekly_index, base_date in enumerate(sunday_dates):
            days_diff = (base_date - r).days
            if days_diff < 7 and days_diff >= 0:
                break

        activity_data = record_data.get("activity", {})
        task_data = activity_data.get("task", [])
        for t in task_data:
            project = t["project"]

            duration = (arrow.get(t["end_time"]) - arrow.get(t["start_time"])).seconds
            duration_hours = round(duration / 60 / 60, 1)

            task_reports[project][weekly_index] += duration_hours

            # Color
            if project not in colors and "color" in t:
                colors[project] = t["color"]

    pie_chart_count = weekly_index + 1

    if start_date.date() == end_date.date():
        COL_COUNT = 1
    else:
        # Default COL_COUNT
        COL_COUNT = 4

    ROW_COUNT = math.ceil(pie_chart_count / COL_COUNT)

    pie_values = []
    for i in range(pie_chart_count):
        pie_values.append([])

    subplots_specs = []
    for r in range(ROW_COUNT):
        row_specs = []
        for c in range(COL_COUNT):
            row_specs.append({"type": "domain"})
        subplots_specs.append(row_specs)

    fig = make_subplots(rows=ROW_COUNT, cols=COL_COUNT, specs=subplots_specs)

    pie_colors = []
    for category, task_values in task_reports.items():
        for i, v in enumerate(task_values):
            pie_values[i].append(v)
        pie_colors.append(colors.get(category, "#DEDEDE"))

    for i, pie_value in enumerate(pie_values):
        col_index = int((i % COL_COUNT)) + 1
        row_index = int((i / COL_COUNT)) + 1
        fig.add_trace(
            go.Pie(
                labels=categories,
                values=pie_value,
                name=sunday_dates[i].format("MMM D"),
            ),
            row=row_index,
            col=col_index,
        )
    # Use `hole` to create a donut-like pie chart
    fig.update_traces(
        hole=.3, hoverinfo="label+percent+name", marker={"colors": pie_colors}
    )
    return fig


def _make_summary_line_fig(start_date, end_date):
    start_date = arrow.get(start_date).replace(tzinfo='Asia/Seoul')
    end_date = arrow.get(end_date).replace(tzinfo='Asia/Seoul')

    summary_data = []

    for r in arrow.Arrow.range("day", start_date, end_date):
        offset_day = (arrow.now() - r).days
        record_data = data_handler.read_record(days=-offset_day)
        if "summary" not in record_data or "total" not in record_data["summary"]:
            record_data = data_handler.read_record(days=-offset_day, redownload=True)
        summary_data.append(record_data.get("summary", {}))

    dates = data_handler.get_daily_base_of_range(start_date, end_date)
    dates = [d.format("YYYY-MM-DD") for d in dates]

    def get_score(data, category):
        return data.get(category, 0)

    attention_scores = [get_score(data, "attention") for data in summary_data]
    happy_scores = [get_score(data, "happy") for data in summary_data]
    productive_scores = [get_score(data, "productive") for data in summary_data]
    sleep_scores = [get_score(data, "sleep") for data in summary_data]
    repeat_task_scores = [get_score(data, "repeat_task") for data in summary_data]
    total_scores = [get_score(data, "total") for data in summary_data]

    names = ["attention", "happy", "productive", "sleep", "repeat_task", "total"]
    ys = [
        attention_scores,
        happy_scores,
        productive_scores,
        sleep_scores,
        repeat_task_scores,
        total_scores,
    ]

    # Create traces
    data = []
    for name, y in zip(names, ys):
        data.append(go.Scatter(x=dates, y=y, mode="lines+markers", name=name))

    layout = go.Layout(
        autosize=True,
        title="Summary Chart",
        xaxis={
            "tickformat":'%m-%d %a'
        }
    )

    fig = go.Figure(data=data, layout=layout)
    return fig


def _make_calendar_heatmap_fig(start_date, end_date):
    start_date = arrow.get(start_date).replace(tzinfo='Asia/Seoul')
    end_date = arrow.get(end_date).replace(tzinfo='Asia/Seoul')

    categories = ["BAT", "Blog", "Diary", "Exercise"]

    dates = []

    z = []
    for _ in categories:
        z.append([])

    for r in arrow.Arrow.range("day", start_date, end_date):
        offset_day = (arrow.now() - r).days
        habit_data = data_handler.read_habit(days=-offset_day)

        for i, category in enumerate(categories):
            category = category.lower()
            do_category = f"do_{category}"
            if do_category in habit_data:  # metric_v0 format
                habit_point = int(habit_data[do_category])
            elif category in habit_data:  # metric_v1 format
                habit_point = int(habit_data[category])
            else:
                habit_point = 0

            z[i].append(habit_point)

        dates.append(r.format("YYYY-MM-DD"))

    categories.append("All")
    z_do_all = []

    for i in range(len(dates)):
        do_all = 0
        for item in z:
            do_all += item[i]
        z_do_all.append(do_all)
    z.append(z_do_all)

    fig = go.Figure(
        data=go.Heatmap(
            z=z,
            text=z,
            x=dates,
            y=categories,
            colorscale=[[0, "#FFFFFF"], [1, "#19410a"]],
            xgap=7,
            ygap=7,
        )
    )

    fig.update_layout(
        title="BAT, Diary, Exercise per day",
        height=300,
        xaxis={
            "tickformat": "%a-%m-%d",
            "tickangle": 75,
            "showticklabels": True,
            "dtick": 86400000.0 * 1,  # 1 day
        },
    )

    return fig


def _make_summary_chart_and_corr(df):
    df["year"] = df["time"].apply(lambda x: str(arrow.get(x).year))
    df["month"] = df["time"].apply(lambda x: arrow.get(x).format("MM"))
    df["day"] = df["time"].apply(lambda x: arrow.get(x).format("DDD"))
    df = df.drop_duplicates(subset=["year", "day"])

    summary_month_df = df.groupby(["year", "month"]).mean().reset_index()
    bar_fig = px.bar(
        summary_month_df,
        x="month",
        y="total_score",
        barmode="group",
        color="year",
        category_orders={
            "category": data_handler.TASK_CATEGORIES,
            "year": ["2017", "2018", "2019", "2020"],
            "weekday": list(calendar.day_name),
        },
    )

    corr_df = df.corr()
    corr_fig = px.imshow(
        corr_df.to_numpy(),
        x=list(corr_df.columns),
        y=list(corr_df.columns),
        color_continuous_scale=px.colors.sequential.Viridis,
    )
    return bar_fig, corr_fig


def _make_sleep_happy_scatter_chart(df):
    jittering_value = 0.4

    df["weekday"] = df["time"].apply(lambda x: calendar.day_name[arrow.get(x).isoweekday()-1])
    df["happy_score"] = df["happy_score"].apply(lambda x: x + random.uniform(-jittering_value, jittering_value))  # Jittering
    df["year"] = df["year"].apply(lambda x: str(x))

    fig = px.scatter(
        df,
        x="sleep_time",
        y="happy_score",
        color="year",
        category_orders={
            "year": ["2017", "2018", "2019", "2020"],
            "weekday": list(calendar.day_name),
        },
        facet_col="weekday",
        facet_col_wrap=4,
        opacity=0.7,
        title=f"SleepTime x Happy Correlation: {df.corr()['sleep_time']['happy_score']}",
    )

    max_sleep_time = df["sleep_time"].max()

    time_values = list(range(0, round(max_sleep_time)+30, 60))
    fig.update_xaxes({
        "tickmode": "array",
        "tickvals": time_values,
        "ticktext": [f"{t//60:02d}:{t%60:02d}" for t in time_values],
    })
    return fig


def _make_sleep_attention_scatter_chart(df):
    jittering_value = 0.4

    df["weekday"] = df["time"].apply(lambda x: calendar.day_name[arrow.get(x).isoweekday()-1])
    df["attention_score"] = df["attention_score"].apply(lambda x: x + random.uniform(-jittering_value, jittering_value))  # Jittering
    df["year"] = df["year"].apply(lambda x: str(x))

    fig = px.scatter(
        df,
        x="sleep_time",
        y="attention_score",
        color="year",
        category_orders={
            "year": ["2017", "2018", "2019", "2020"],
            "weekday": list(calendar.day_name),
        },
        facet_col="weekday",
        facet_col_wrap=4,
        opacity=0.7,
        title=f"SleepTime x Attention Correlation: {df.corr()['sleep_time']['attention_score']}",
    )

    max_sleep_time = df["sleep_time"].max()

    time_values = list(range(0, round(max_sleep_time)+30, 60))
    fig.update_xaxes({
        "tickmode": "array",
        "tickvals": time_values,
        "ticktext": [f"{t//60:02d}:{t%60:02d}" for t in time_values],
    })
    return fig


def _make_task_working_hour_bar_chart(df):
    df["year"] = df["end_time"].apply(lambda x: str(arrow.get(x).year))
    df["month"] = df["end_time"].apply(lambda x: arrow.get(x).format("MM"))
    df["working_hour"] = df.apply(lambda x: (arrow.get(x.end_time) - arrow.get(x.start_time)).seconds / 3600, axis=1)
    df["category"] = df["project"]

    df = df.groupby(["year", "month", "category"]).sum().reset_index()

    colors = {
        'Empty': '#DEDEDE',
        'Article': '#e36a00',
        'Review': '#566614',
        'Book': '#bf7000',
        'Management': '#990099',
        'Develop': '#0b83d9',
        'Meeting': '#9e5bd9',
        'Think': '#2da608',
        'Seminar': '#06a893',
        'Blog': '#566614',
        'Exercise': '#525266',
        'Research': '#465bb3',
        'MOOC': '#06a893',
        'Planning': '#d94182'
    }

    fig = px.bar(
        df,
        x="month",
        y="working_hour",
        color="category",
        color_discrete_map=colors,
        category_orders={
            "category": data_handler.TASK_CATEGORIES,
            "year": ["2017", "2018", "2019", "2020"],
            "weekday": list(calendar.day_name),
        },
        facet_row="year",
        height=800,
    )
    return fig


def _make_task_scatter_chart(df, task_working_minutes):
    df["date"] = df["end_time"].apply(lambda x: arrow.get(x).format("YYYY-MM-DD"))
    # df["start_time"] = df["start_time"].apply(lambda x: arrow.get(x).hour * 60 + arrow.get(x).minute)
    df["working_minutes"] = df.apply(lambda x: int((arrow.get(x.end_time) - arrow.get(x.start_time)).seconds / 60), axis=1)
    df["working_hours"] = df["working_minutes"].apply(lambda x: f"{x//60}:{x%60:02d}")

    df["category"] = df["project"]
    df["size"] = df["working_minutes"].apply(lambda x: x/40)

    df = df.loc[(df["working_minutes"] >= task_working_minutes[0]) & (df["working_minutes"] <= task_working_minutes[1])]

    jittering_value = 0.35
    df[['attention_score']] = df[['score']].fillna(value=3)
    df["attention_score_j"] = df["attention_score"].apply(lambda x: x + random.uniform(-jittering_value, jittering_value))  # Jittering

    df[['happy_score']] = df[['happy_score']].fillna(value=3)
    df["happy_score_j"] = df["happy_score"].apply(lambda x: x + random.uniform(-jittering_value, jittering_value))  # Jittering

    colors = {
        'Empty': '#DEDEDE',
        'Article': '#e36a00',
        'Review': '#566614',
        'Book': '#bf7000',
        'Management': '#990099',
        'Develop': '#0b83d9',
        'Meeting': '#9e5bd9',
        'Think': '#2da608',
        'Seminar': '#06a893',
        'Blog': '#566614',
        'Exercise': '#525266',
        'Research': '#465bb3',
        'MOOC': '#06a893',
        'Planning': '#d94182'
    }

    fig = px.scatter(
        df,
        x="happy_score_j",
        y="attention_score_j",
        size="size",
        size_max=15,
        color="category",
        color_discrete_map=colors,
        category_orders={
            "category": data_handler.TASK_CATEGORIES,
            "year": ["2017", "2018", "2019", "2020"],
            "weekday": list(calendar.day_name),
        },
        hover_data=["start_time", "end_time", "description", "attention_score", "happy_score", "working_hours"],
        height=700,
        opacity=0.5,
        range_x=[0.5, 5.5],
        range_y=[0.5, 5.5],
    )

    time_values = list(range(0, 1440+1, 60))
    fig.update_xaxes({
        "tickmode": "array",
        "tickvals": time_values,
        "ticktext": [f"{t//60:02d}:{t%60:02d}" for t in time_values],
    })
    return fig
