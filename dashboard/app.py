# -*- coding: utf-8 -*-

import arrow

import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
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
from data_handler import DataHandler
from date_unit import DateUnit


app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.config["suppress_callback_exceptions"] = True

data_handler = DataHandler()
kpi = data_handler.read_kpi()


DAILY_TAP = "daily"
WEEKLY_TAP = "weekly"
MONTHLY_TAP = "monthly"
QUATERLY_TAP = "quarterly"

habit_tab_list = [
    DAILY_TAP,
    WEEKLY_TAP
]

tab_list = habit_tab_list

# the style arguments for the sidebar. We use position:fixed and a fixed width
SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "16rem",
    "padding": "2rem 1rem",
}

# the styles for the main content position it to the right of the sidebar and
# add some padding.
CONTENT_STYLE = {
    "margin-left": "17rem",
    "padding": "2rem 1rem",
    "background-color": "#f4f7fc",
}

DATE_PICKER_STYLE = {
    "text-align": "center",
    "width": "100%",
    "margin-bottom": "15px",
}


sidebar = html.Div(
    [
        html.A(
            html.H2("Quantified Self", className="display-5"),
            href="/",
            style={"text-decoration": "none"},
        ),
        html.Hr(),
        html.P("Habits", className="lead"),
        dbc.Nav(
            [
                dbc.NavLink(tab.capitalize(), href=f"/{tab}", id=f"{tab}-link")
                for tab in habit_tab_list
            ],
            vertical=True,
            pills=True,
        ),

        html.P("Sleep", className="lead", style={"margin-top": "10px"}),

        # Interval
        dcc.Interval(
            id="interval-component-10min",
            interval=10 * 60 * 1000,  # every 10 mins
            n_intervals=0,
        ),
    ],
    style=SIDEBAR_STYLE,
)

content = html.Div(id="page-content", style=CONTENT_STYLE)

app.layout = html.Div([dcc.Location(id="url"), sidebar, content])

# this callback uses the current pathname to set the active state of the
# corresponding nav link to true, allowing users to tell see page they are on
@app.callback(
    [Output(f"{tab}-link", "active") for tab in tab_list], [Input("url", "pathname")]
)
def toggle_active_links(pathname):
    if pathname == "/":
        return [False] * len(tab_list)
    return [pathname == f"/{tab}" for tab in tab_list]


def make_card_html(
    body,
    card_id=None,
    title_text=None,
    size=12,
    background_color="white",
    class_name="",
):

    card_html = html.Div(
        [html.Div([], className="card mb-3 text-center")],
        className=f"col-sm-{size}",
    )
    if card_id is None:
        div = html.Div(
            body,
            className="card-body " + class_name,
            style={"background-color": background_color}
        )
    else:
        div = html.Div(
            body,
            id=card_id,
            className="card-body " + class_name,
            style={"background-color": background_color}
        )

    card_html.children[0].children.append(div)

    if title_text is not None:
        title = html.H6(title_text, className="card-title")
        card_html.children[0].children[0].children.insert(0, title)

    return card_html


@app.callback(Output("page-content", "children"), [Input("url", "pathname")])
def render_page_content(pathname):

    if pathname == "/":  # Dashboard Tab

        # Daily Dashboard
        daily_task_hour_card = make_card_html(
            [
                html.P(id="daily_task_hour_value"),
            ],
            card_id="daily_task_hour_card",
            title_text="Task Hour",
            size=2,
        )

        daily_sleep_hour_card = make_card_html(
            [
                html.P(id="daily_sleep_hour_value")
            ],
            card_id="daily_sleep_hour_card",
            title_text="Sleep Hour",
            size=2,
        )

        daily_remain_hour_card = make_card_html(
            [
                html.P(id="daily_remain_hour_value")
            ],
            card_id="daily_remain_hour_card",
            title_text="Remain Hour",
            size=2
        )

        daily_exercise_card = make_card_html(
            [
                html.P(id="daily_exercise_value")
            ],
            card_id="daily_exercise_card",
            title_text="Exercise",
            size=2
        )

        daily_diary_card = make_card_html(
            [
                html.P(id="daily_diary_value")
            ],
            card_id="daily_diary_card",
            title_text="Diary",
            size=2
        )

        daily_bat_card = make_card_html(
            [
                html.P(id="daily_bat_value")
            ],
            card_id="daily_bat_card",
            title_text="BAT",
            size=2
        )

        # Weekly Dashboard
        weekly_task_total_hour_card = make_card_html(
            [
                html.P(id="weekly_task_total_hour_value")
            ],
            card_id="weekly_task_total_hour_card",
            title_text="Total Hour",
            size=3
        )

        weekly_exercise_card = make_card_html(
            [
                html.P(id="weekly_exercise_count_value")
            ],
            card_id="weekly_exercise_count_card",
            title_text="Exercise Count",
            size=3
        )

        weekly_diary_card = make_card_html(
            [
                html.P(id="weekly_diary_count_value")],
            card_id="weekly_diary_count_card",
            title_text="Diary Count",
            size=3
        )

        weekly_bat_card = make_card_html(
            [
                html.P(id="weekly_bat_count_value")],
            card_id="weekly_bat_count_card",
            title_text="BAT Count",
            size=3
        )

        dashboard_div = html.Div([
            html.H2("Habits", className="col-sm-12"),
        ])
        dashboard_div.children.extend([
            make_card_html([
                html.Div([
                    html.H3("Daily"),
                    html.Hr(),
                ], className="col-sm-12"),
                daily_task_hour_card,
                daily_sleep_hour_card,
                daily_remain_hour_card,
                daily_exercise_card,
                daily_diary_card,
                daily_bat_card,
            ],
            class_name="container-fluid row")
        ])

        weekly_dashboard_items =[
            html.Div([
                html.H3("Weekly", className="col-sm-12"),
                html.Hr(),
            ], className="col-sm-12"),
            weekly_task_total_hour_card,
            weekly_exercise_card,
            weekly_diary_card,
            weekly_bat_card,

            html.Div([
                html.Hr(),
            ], className="col-sm-12", style={"margin-bottom": "15px"}),
        ]

        # Weekly Task Category
        for task_category in data_handler.TASK_CATEGORIES:
            task_category_lower = task_category.lower()
            weekly_dashboard_items.append(
                make_card_html(
                    [
                        html.P(id=f"weekly_{task_category_lower}_value")
                    ],
                    card_id=f"weekly_{task_category_lower}_card",
                    title_text=task_category,
                    size=2
                )
            )

        weekly_dashboard_card = make_card_html(
            weekly_dashboard_items,
            class_name="container-fluid row",
        )
        dashboard_div.children.append(weekly_dashboard_card)

        return dashboard_div

    elif pathname == f"/{DAILY_TAP}":

        # Daily - Schedule * Pie Chart
        daily_schedule_card = make_card_html(
            [
                html.Div(
                    [
                        html.Span(
                            "Date:", style={"font-size": "1.5em", "margin-right": "5px"}
                        ),
                        dcc.DatePickerSingle(
                            id="date-picker-daily-schedule",
                            date=arrow.now().datetime,
                            max_date_allowed=arrow.now().datetime,
                        ),
                    ],
                    style=DATE_PICKER_STYLE,
                ),
                make_card_html([
                    dcc.Graph(id="live-daily-schedule"),
                ],
                size=8),
                make_card_html([
                    dcc.Graph(id="live-daily-task-pie-reports"),
                ], size=4),
            ],
            class_name="container-fluid row"
        )

        # Daily - Calendar Heatmap
        daily_cal_heatmap_card = make_card_html(
            [
                html.Div(
                    [
                        html.Span(
                            "DateRange:",
                            style={"font-size": "1.5em", "margin-right": "5px"},
                        ),
                        dcc.DatePickerRange(
                            id="date-picker-range-calendar-heatmap",
                            first_day_of_week=1,  # Monday
                            start_date=arrow.now().shift(days=-30).datetime,
                            end_date=arrow.now().datetime,
                            max_date_allowed=arrow.now().datetime,
                        ),
                    ],
                    style=DATE_PICKER_STYLE,
                ),
                dcc.Graph(id="live-calendar-heatmap"),
            ]
        )

        # Daily Task - Stack Bar Chart
        # Daily Summary Chart
        now = arrow.now()
        before_7_days = now.shift(days=-7)

        daily_summary_and_task_card = make_card_html(
            [
                html.Div(
                    [
                        html.Span(
                            "DateRange:",
                            style={"font-size": "1.5em", "margin-right": "5px"},
                        ),
                        dcc.DatePickerRange(
                            id="date-picker-range-daily",
                            first_day_of_week=1,  # Monday
                            start_date=before_7_days.datetime,
                            end_date=now.datetime,
                            max_date_allowed=arrow.now().datetime,
                        ),
                    ],
                    style=DATE_PICKER_STYLE,
                ),
                make_card_html([
                    dcc.Graph(id="live-daily-stack-reports"),
                ], size=6),
                make_card_html([
                    dcc.Graph(id="live-daily-chart"),
                ], size=6),
            ],
            class_name="container-fluid row"
        )

        return html.Div(
            [
                daily_schedule_card,
                daily_cal_heatmap_card,
                daily_summary_and_task_card,
            ],
            className="container-fluid row",
        )

    elif pathname == f"/{WEEKLY_TAP}":

        now = arrow.now()
        remain_days = 21 + now.weekday()
        before_4_weeks = now.shift(days=-remain_days)

        # Weekly Task - Stack Bar Chart
        weekly_task_card = make_card_html(
            [
                html.Div(
                    [
                        html.Span(
                            "DateRange:",
                            style={"font-size": "1.5em", "margin-right": "5px"},
                        ),
                        dcc.DatePickerRange(
                            id="date-picker-range-weekly",
                            first_day_of_week=1,  # Monday
                            start_date=before_4_weeks.datetime,
                            end_date=now.datetime,
                            max_date_allowed=arrow.now().datetime,
                        ),
                    ],
                    style=DATE_PICKER_STYLE,
                ),
                dcc.Graph(id="live-weekly-stack-reports"),
                dcc.Graph(id="live-weekly-task-pie-reports"),
            ]
        )

        return html.Div(
            [
                weekly_task_card,
            ],
            className="container-fluid row",
        )

    elif pathname == "tab-2":
        return html.Div([html.H3("Tab content 2")])


"""
    Dashboard
"""


@app.callback(
    [
        Output(component_id='daily_task_hour_card', component_property='style'),
        Output(component_id='daily_task_hour_value', component_property='children'),
        Output(component_id='daily_sleep_hour_card', component_property='style'),
        Output(component_id='daily_sleep_hour_value', component_property='children'),
        Output(component_id='daily_remain_hour_card', component_property='style'),
        Output(component_id='daily_remain_hour_value', component_property='children'),
        Output(component_id='daily_exercise_card', component_property='style'),
        Output(component_id='daily_exercise_value', component_property='children'),
        Output(component_id='daily_diary_card', component_property='style'),
        Output(component_id='daily_diary_value', component_property='children'),
        Output(component_id='daily_bat_card', component_property='style'),
        Output(component_id='daily_bat_value', component_property='children'),
    ],
    [Input(component_id='interval-component-10min', component_property='n_intervals')]
)
def update_daily(n):
    return _update_daily(kpi["daily"])


@app.callback(
    [
        Output(component_id='weekly_bat_count_card', component_property='style'),
        Output(component_id='weekly_bat_count_value', component_property='children'),
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
    Habit - Daily Tab
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
