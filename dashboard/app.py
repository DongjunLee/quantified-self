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

    _make_summary_chart_and_corr,
    _make_summary_line_chart,
    _make_summary_exercise_all_score_bar_charts,
    _make_sleep_happy_scatter_chart,
    _make_sleep_attention_scatter_chart,
    _make_task_working_hour_bar_chart,
    _make_task_ranking_table_chart,
    _make_task_scatter_chart_and_corr,
)
from dashboard import (
    _update_daily,
    _update_weekly,
    _update_weekly_task_category,
)
from index import (
    TAB_LIST,
    OVERVIEW_TAP,
    SUMMARY_TAP,
    TASK_TAP,
    SLEEP_TAP,

    make_app_layout,
    make_overview_content,
    make_summary_content,
    make_task_content,
    make_sleep_content,
)
from data_handler import DataHandler
from date_unit import DateUnit


app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.config["suppress_callback_exceptions"] = True

data_handler = DataHandler()
kpi = data_handler.read_kpi()
metric_dfs = data_handler.read_record_df_by_metrics()

tab_list = TAB_LIST
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
    if pathname == "/":  # Home Tab
        pathname = f"/{OVERVIEW_TAP}"  # NOTE: default tab

    tab_contents = [
        (OVERVIEW_TAP, make_overview_content),
        (SUMMARY_TAP, make_summary_content),
        (TASK_TAP, make_task_content),
        (SLEEP_TAP, make_sleep_content),
    ]

    for (tab, content_function) in tab_contents:
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
        Input("daily-schedule-date-picker", "date"),
    ],
)
def make_daily_schedule_fig(n, date):
    return _make_daily_schedule_fig(date)


@app.callback(
    Output("live-daily-task-pie-reports", "figure"),
    [
        Input("interval-component-10min", "n_intervals"),
        Input("daily-schedule-date-picker", "date"),
    ],
)
def make_daily_pie_chart_fig(n, date):
    return _make_pie_chart_fig(date, date)


@app.callback(
    Output("live-calendar-heatmap", "figure"),
    [
        Input("interval-component-10min", "n_intervals"),
        Input("daily-habit-date-range", "start_date"),
        Input("daily-habit-date-range", "end_date"),
    ],
)
def make_calendar_heatmap_fig(n, start_date, end_date):
    return _make_calendar_heatmap_fig(start_date, end_date)


@app.callback(
    Output("live-daily-task-stack-bar", "figure"),
    [
        Input("interval-component-10min", "n_intervals"),
        Input("daily-task-summary-date-range", "start_date"),
        Input("daily-task-summary-date-range", "end_date"),
    ],
)
def make_daily_task_stacked_bar_fig(n, start_date, end_date):
    return _make_task_stacked_bar_fig(start_date, end_date, date_unit=DateUnit.DAILY)



@app.callback(
    Output("live-daily-summary-line", "figure"),
    [
        Input("interval-component-10min", "n_intervals"),
        Input("daily-task-summary-date-range", "start_date"),
        Input("daily-task-summary-date-range", "end_date"),
    ]
)
def make_daily_line_fig(n, start_date, end_date):
    return _make_summary_line_fig(start_date, end_date)



"""
    Habit - Weekly Tab
"""

@app.callback(
    Output("live-weekly-task-stack-bar", "figure"),
    [
        Input("interval-component-10min", "n_intervals"),
        Input("weekly-task-bar-pie-date-range", "start_date"),
        Input("weekly-task-bar-pie-date-range", "end_date"),
    ],
)
def make_weekly_task_stacked_bar_fig(n, start_date, end_date):
    return _make_task_stacked_bar_fig(start_date, end_date, date_unit=DateUnit.WEEKLY)


@app.callback(
    Output("live-weekly-task-pie", "figure"),
    [
        Input("interval-component-10min", "n_intervals"),
        Input("weekly-task-bar-pie-date-range", "start_date"),
        Input("weekly-task-bar-pie-date-range", "end_date"),
    ],
)
def make_weekly_pie_chart_fig(n, start_date, end_date):
    return _make_pie_chart_fig(start_date, end_date)


@app.callback(
    [
        Output("summary-total-monthly-chart", "figure"),
        Output("summary-correlation-chart", "figure"),
    ],
    [
        Input("metric_dropdown", "value"),
    ],
)
def make_summary_bar_chart_fig(metric):
    return _make_summary_chart_and_corr(metric_dfs[metric]["daily_summary"])


@app.callback(
    Output("summary-total-line-chart", "figure"),
    [
        Input("metric_dropdown", "value"),
    ],
)
def make_summary_line_chart_fig(metric):
    return _make_summary_line_chart(metric_dfs[metric]["daily_summary"])


@app.callback(
    [
        Output("summary-exercise-do-or-not-attention-chart", "figure"),
        Output("summary-exercise-do-or-not-happy-chart", "figure"),
    ],
    [
        Input("metric_dropdown", "value"),
    ],
)
def make_summary_exercise_chart_fig(metric):
    return _make_summary_exercise_all_score_bar_charts(metric_dfs[metric]["daily_summary"])


@app.callback(
    Output("task-category-working-hour-monthly-chart", "figure"),
    [
        Input("interval-component-10min", "n_intervals"),
    ],
)
def make_task_working_hour_chart_fig(n):
    return _make_task_working_hour_bar_chart(metric_dfs["all"]["task_activity"])


@app.callback(
    Output("task-working-hour-yearly-chart", "figure"),
    [
        Input("year_dropdown", "value"),
    ],
)
def make_task_working_hour_yearly_chart_fig(year):
    return _make_task_ranking_table_chart(metric_dfs["all"]["task_activity"], year)


@app.callback(
    [
        Output("task-scatter-chart", "figure"),
        Output("task-correlation-chart", "figure"),
    ],
    [
        Input("color-dropdown", "value"),
        Input("year-checklist", "value"),
        Input("weekday-checklist", "value"),
        Input("task-category-checklist", "value"),
        Input("task-start-hour-slider", "value"),
    ],
)
def make_task_scatter_chart_fig(color, year, weekday, category, start_hour_intervals):
    return _make_task_scatter_chart_and_corr(
        metric_dfs["all"]["task_activity"],
        color,
        year,
        weekday,
        category,
        start_hour_intervals
    )


@app.callback(
    Output("sleep-hour-happy-scatter-chart", "figure"),
    [
        Input("metric_dropdown", "value"),
    ],
)
def make_sleep_happy_scatter_chart_fig(metric):
    return _make_sleep_happy_scatter_chart(metric_dfs[metric]["sleep_activity"])


@app.callback(
    Output("sleep-hour-attention-scatter-chart", "figure"),
    [
        Input("metric_dropdown", "value"),
    ],
)
def make_sleep_attention_scatter_chart_fig(metric):
    return _make_sleep_attention_scatter_chart(metric_dfs[metric]["sleep_activity"])




if __name__ == "__main__":
    app.run_server(debug=True, host="0.0.0.0", port=8000)
