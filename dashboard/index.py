
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html

from data_handler import DataHandler


HABITS_DAILY_TAP = "habits_daily"
HABITS_WEEKLY_TAP = "habits_weekly"
HABITS_ANALYSIS_TAP = "habits_analysis"

HABITS_TAB_LIST = [
    HABITS_DAILY_TAP,
    HABITS_WEEKLY_TAP,
    HABITS_ANALYSIS_TAP,
]


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


data_handler = DataHandler()


def make_app_layout():
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
                    dbc.NavLink(tab.split("_")[1].capitalize(), href=f"/{tab}", id=f"{tab}-link")
                    for tab in HABITS_TAB_LIST
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

    layout = html.Div([
        dcc.Location(id="url"),
        sidebar,
        content,
    ])
    return layout


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


def make_dashboard_content():
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

    daily_bat_card = make_card_html(
        [
            html.P(id="daily_bat_value")
        ],
        card_id="daily_bat_card",
        title_text="BAT",
        size=2
    )

    daily_blog_card = make_card_html(
        [
            html.P(id="daily_blog_value")
        ],
        card_id="daily_blog_card",
        title_text="Blog",
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

    daily_exercise_card = make_card_html(
        [
            html.P(id="daily_exercise_value")
        ],
        card_id="daily_exercise_card",
        title_text="Exercise",
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

    weekly_bat_card = make_card_html(
        [
            html.P(id="weekly_bat_count_value")],
        card_id="weekly_bat_count_card",
        title_text="BAT Count",
        size=2
    )

    weekly_blog_card = make_card_html(
        [
            html.P(id="weekly_blog_count_value")],
        card_id="weekly_blog_count_card",
        title_text="Blog Count",
        size=2
    )

    weekly_diary_card = make_card_html(
        [
            html.P(id="weekly_diary_count_value")],
        card_id="weekly_diary_count_card",
        title_text="Diary Count",
        size=2
    )

    weekly_exercise_card = make_card_html(
        [
            html.P(id="weekly_exercise_count_value")
        ],
        card_id="weekly_exercise_count_card",
        title_text="Exercise Count",
        size=2
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
            daily_bat_card,
            daily_blog_card,
            daily_diary_card,
            daily_exercise_card,
        ],
        class_name="container-fluid row")
    ])

    weekly_dashboard_items =[
        html.Div([
            html.H3("Weekly", className="col-sm-12"),
            html.Hr(),
        ], className="col-sm-12"),
        weekly_task_total_hour_card,
        weekly_bat_card,
        weekly_blog_card,
        weekly_diary_card,
        weekly_exercise_card,
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
                size=3
            )
        )

    weekly_dashboard_card = make_card_html(
        weekly_dashboard_items,
        class_name="container-fluid row",
    )
    dashboard_div.children.append(weekly_dashboard_card)

    return dashboard_div


def make_habits_daily_content(now):
    before_7_days = now.shift(days=-7)
    before_30_days = now.shift(days=-30)

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
                        date=now.datetime,
                        max_date_allowed=now.datetime,
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
                        start_date=before_30_days.datetime,
                        end_date=now.datetime,
                        max_date_allowed=now.datetime,
                    ),
                ],
                style=DATE_PICKER_STYLE,
            ),
            dcc.Graph(id="live-calendar-heatmap"),
        ]
    )

    # Daily Task - Stack Bar Chart
    # Daily Summary Chart
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
                        max_date_allowed=now.datetime,
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


def make_habits_weekly_content(now):
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
                        max_date_allowed=now.datetime,
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


def make_habits_analysis_content(now):
    # TODO:

    return html.Div(
        [
        ],
        className="container-fluid row",
    )
