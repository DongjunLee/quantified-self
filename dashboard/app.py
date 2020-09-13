# -*- coding: utf-8 -*-

import arrow

import dash
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output

from chart import (
    _make_daily_schedule_fig,
    _make_task_stacked_bar_fig,
    _make_pie_chart_fig,
    _make_summary_line_fig,
    _make_calendar_heatmap_fig,
)
from dashboard import (
    _update_daily,
    _update_weekly,
    _update_weekly_task_category,
)
from index import (
    HABITS_DAILY_TAP,
    HABITS_WEEKLY_TAP,
    HABITS_ANALYSIS_TAP,
    HABITS_TAB_LIST,
    make_app_layout,
    make_dashboard_content,
    make_habits_daily_content,
    make_habits_weekly_content,
    make_habits_analysis_content,
)
from data_handler import DataHandler
from date_unit import DateUnit


app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.config["suppress_callback_exceptions"] = True

data_handler = DataHandler()
kpi = data_handler.read_kpi()

tab_list = HABITS_TAB_LIST
app.layout = make_app_layout()

# this callback uses the current pathname to set the active state of the
# corresponding nav link to true, allowing users to tell see page they are on
@app.callback(
    [Output(f"{tab}-link", "active") for tab in tab_list],
    [Input("url", "pathname")]
)
def toggle_active_links(pathname):
    if pathname == "/":
        return [False] * len(tab_list)
    return [pathname == f"/{tab}" for tab in tab_list]


@app.callback(Output("page-content", "children"), [Input("url", "pathname")])
def render_page_content(pathname):

    if pathname == "/":  # Dashboard Tab
        return make_dashboard_content()

    habit_tab_contents = [
        (HABITS_DAILY_TAP, make_habits_daily_content),
        (HABITS_WEEKLY_TAP, make_habits_weekly_content),
        (HABITS_ANALYSIS_TAP, make_habits_analysis_content),
    ]

    for (tab, content_function) in habit_tab_contents:
        if pathname == f"/{tab}":
            return content_function(arrow.now())


"""
    Dashboard
"""


@app.callback(
    [
        Output(component_id='daily_task_hour_card', component_property='style'),
        Output(component_id='daily_task_hour_value', component_property='children'),
        Output(component_id='daily_sleep_hour_card', component_property='style'),
        Output(component_id='daily_sleep_hour_value', component_property='children'),
        Output(component_id='daily_bat_card', component_property='style'),
        Output(component_id='daily_bat_value', component_property='children'),
        Output(component_id='daily_blog_card', component_property='style'),
        Output(component_id='daily_blog_value', component_property='children'),
        Output(component_id='daily_diary_card', component_property='style'),
        Output(component_id='daily_diary_value', component_property='children'),
        Output(component_id='daily_exercise_card', component_property='style'),
        Output(component_id='daily_exercise_value', component_property='children'),
    ],
    [Input(component_id='interval-component-10min', component_property='n_intervals')]
)
def update_daily(n):
    return _update_daily(kpi["daily"])


@app.callback(
    [
        Output(component_id='weekly_bat_count_card', component_property='style'),
        Output(component_id='weekly_bat_count_value', component_property='children'),
        Output(component_id='weekly_blog_count_card', component_property='style'),
        Output(component_id='weekly_blog_count_value', component_property='children'),
        Output(component_id='weekly_diary_count_card', component_property='style'),
        Output(component_id='weekly_diary_count_value', component_property='children'),
        Output(component_id='weekly_exercise_count_card', component_property='style'),
        Output(component_id='weekly_exercise_count_value', component_property='children'),
    ],
    [Input(component_id='interval-component-10min', component_property='n_intervals')]
)
def update_weekly(n):
    return _update_weekly(kpi["weekly"])


@app.callback(
    [
        Output(component_id='weekly_task_total_hour_card', component_property='style'),
        Output(component_id='weekly_task_total_hour_value', component_property='children'),
    ] + [
        Output(component_id=f"weekly_{task_category.lower()}_{id_str}", component_property=property_str)
        for task_category in data_handler.TASK_CATEGORIES
        for (id_str, property_str) in [("card", "style"), ("value", "children")]
    ],
    [Input(component_id='interval-component-10min', component_property='n_intervals')]
)
def update_weekly_task_category(n):
    return _update_weekly_task_category(kpi["weekly"])



"""
    Habits - Daily Tab
"""


@app.callback(
    Output("live-daily-schedule", "figure"),
    [
        Input("interval-component-10min", "n_intervals"),
        Input("date-picker-daily-schedule", "date"),
    ],
)
def make_daily_schedule_fig(n, date):
    return _make_daily_schedule_fig(date)


@app.callback(
    Output("live-daily-task-pie-reports", "figure"),
    [
        Input("interval-component-10min", "n_intervals"),
        Input("date-picker-daily-schedule", "date"),
    ],
)
def make_daily_pie_chart_fig(n, date):
    return _make_pie_chart_fig(date, date)


@app.callback(
    Output("live-daily-chart", "figure"),
    [
        Input("interval-component-10min", "n_intervals"),
        Input("date-picker-range-daily", "start_date"),
        Input("date-picker-range-daily", "end_date"),
    ]
)
def make_daily_line_fig(n, start_date, end_date):
    return _make_summary_line_fig(start_date, end_date)


@app.callback(
    Output("live-daily-stack-reports", "figure"),
    [
        Input("interval-component-10min", "n_intervals"),
        Input("date-picker-range-daily", "start_date"),
        Input("date-picker-range-daily", "end_date"),
    ],
)
def make_daily_task_stacked_bar_fig(n, start_date, end_date):
    return _make_task_stacked_bar_fig(start_date, end_date, date_unit=DateUnit.DAILY)


@app.callback(
    Output("live-calendar-heatmap", "figure"),
    [
        Input("interval-component-10min", "n_intervals"),
        Input("date-picker-range-calendar-heatmap", "start_date"),
        Input("date-picker-range-calendar-heatmap", "end_date"),
    ],
)
def make_calendar_heatmap_fig(n, start_date, end_date):
    return _make_calendar_heatmap_fig(start_date, end_date)


"""
    Habit - Weekly Tab
"""

@app.callback(
    Output("live-weekly-stack-reports", "figure"),
    [
        Input("interval-component-10min", "n_intervals"),
        Input("date-picker-range-weekly", "start_date"),
        Input("date-picker-range-weekly", "end_date"),
    ],
)
def make_weekly_task_stacked_bar_fig(n, start_date, end_date):
    return _make_task_stacked_bar_fig(start_date, end_date, date_unit=DateUnit.WEEKLY)


@app.callback(
    Output("live-weekly-task-pie-reports", "figure"),
    [
        Input("interval-component-10min", "n_intervals"),
        Input("date-picker-range-weekly", "start_date"),
        Input("date-picker-range-weekly", "end_date"),
    ],
)
def make_weekly_pie_chart_fig(n, start_date, end_date):
    return _make_pie_chart_fig(start_date, end_date)



if __name__ == "__main__":
    app.run_server(debug=True, host="0.0.0.0", port=8000)
