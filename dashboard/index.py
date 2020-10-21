import arrow
import calendar

import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html

from card import (
    make_card_html,
    simple_value_card,
    row_card,
    chart_card,
    date_picker_with_chart_card,
    date_range_with_chart_card,
)
from data_handler import DataHandler


OVERVIEW_TAP = "overview"
SUMMARY_TAP = "summary"
TASK_TAP = "task"
SLEEP_TAP = "sleep"


TAB_LIST = [
    OVERVIEW_TAP,
    SUMMARY_TAP,
    TASK_TAP,
    SLEEP_TAP,
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
            # html.P("Habits", className="lead"),
            dbc.Nav(
                [
                    dbc.NavLink(f" - {tab.capitalize()}", href=f"/{tab}", id=f"{tab}-link")
                    for tab in TAB_LIST
                ],
                vertical=True,
                pills=True,
            ),

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


def make_overview_content(now):
    # Daily Basis
    daily_basis_cards = [
        simple_value_card(
            "daily_task_hour_card",
            "daily_task_hour_value",
            "작업 시간"
        ),
        simple_value_card(
            "daily_sleep_hour_card",
            "daily_sleep_hour_value",
            "수면 시간"
        ),
        simple_value_card(
            "daily_bat_card",
            "daily_bat_value",
            "BAT"
        ),
        simple_value_card(
            "daily_blog_card",
            "daily_blog_value",
            "Blog"
        ),
        simple_value_card(
            "daily_diary_card",
            "daily_diary_value",
            "일기"
        ),
        simple_value_card(
            "daily_exercise_card",
            "daily_exercise_value",
            "운동"
        )
    ]

    daily_schedule_and_task_pie_cards = date_picker_with_chart_card(
        "daily-schedule-date-picker",
        [
            chart_card("live-daily-schedule", size=8),
            chart_card("live-daily-task-pie-reports", size=4),
        ]
    )

    daily_habit_cards = date_range_with_chart_card(
        "daily-habit-date-range",
        [chart_card("live-calendar-heatmap", size=12)]
    )

    daily_task_and_summary_cards = date_range_with_chart_card(
        "daily-task-summary-date-range",
        [
            chart_card("live-daily-task-stack-bar", size=6),
            chart_card("live-daily-summary-line", size=6),
        ],
        start_date=arrow.now().shift(days=-7)
    )

    # Weekly Basis
    weekly_basis_cards = [
        simple_value_card(
            "weekly_task_total_hour_card",
            "weekly_task_total_hour_value",
            "총 작업 시간"
        ),
        simple_value_card(
            "weekly_bat_count_card",
            "weekly_bat_count_value",
            "BAT 진행 수"
        ),
        simple_value_card(
            "weekly_blog_count_card",
            "weekly_blog_count_value",
            "Blog 진행 수"
        ),
        simple_value_card(
            "weekly_diary_count_card",
            "weekly_diary_count_value",
            "Diary 진행 수"
        ),
        simple_value_card(
            "weekly_exercise_count_card",
            "weekly_exercise_count_value",
            "운동 진행 수"
        ),
    ]

    remain_days = 21 + now.weekday()
    before_4_weeks = now.shift(days=-remain_days)
    before_4_weeks = before_4_weeks.replace(hour=0, minute=0, second=0)

    weekly_task_and_pie_cards = date_range_with_chart_card(
        "weekly-task-bar-pie-date-range",
        [
            chart_card("live-weekly-task-stack-bar", size=12),
            chart_card("live-weekly-task-pie", size=12),
        ],
        start_date=before_4_weeks,  # Start from monday
    )

    # Weekly Task Category
    weekly_task_hour_cards = []
    for task_category in data_handler.TASK_CATEGORIES:
        task_category_lower = task_category.lower()
        weekly_task_hour_cards.append(
            simple_value_card(
                f"weekly_{task_category_lower}_card",
                f"weekly_{task_category_lower}_value",
                task_category,
                size=3
            )
        )

    return html.Div([
        row_card(
            daily_basis_cards,
            title_text="Daily",
            description_text="하루를 기준으로 대쉬보드와 차트가 구성됩니다.",
        ),
        row_card(
            daily_schedule_and_task_pie_cards,
        ),
        row_card(
            daily_habit_cards,
        ),
        row_card(
            daily_task_and_summary_cards,
        ),
        row_card(
            weekly_basis_cards,
            title_text="Weekly",
            description_text="일주일를 기준으로 대쉬보드와 차트가 구성됩니다. (시작일: 월요일)"
        ),
        row_card(
            weekly_task_and_pie_cards,
        ),
        row_card(
            weekly_task_hour_cards,
            title_text="Weekly Task Category 별",
            description_text="일주일를 기준으로 작업 시간과 내역들 (시작일: 월요일)"
        )

    ], className="container-fluid")


def make_summary_content(now):

    return html.Div([
        html.H4("Metric:"),
        dcc.Dropdown(
            id='metric_dropdown',
            options=[
                {'label': 'Metric_v0', 'value': 'metric_v0'},
                {'label': 'Metric_v1', 'value': 'metric_v1'},
            ],
            value='metric_v0',
            style={"width": "200px"},
        ),
        row_card([
            chart_card(
                "summary-total-monthly-chart",
                title_text="Summary: Month x Total Average",
                description_text="월간 종합점수와 평균점수의 변화",
                size=6,
            ),
            chart_card(
                "summary-correlation-chart",
                title_text="Summary: Correlation",
                description_text="하루의 점수와 각종 데이터들 간의 상관관계",
                size=6,
            ),
            chart_card(
                "summary-total-line-chart",
                title_text="Summary: All Score",
                description_text="모든 점수의 변화",
                size=12,
            ),
        ]),
        row_card([
            chart_card(
                "summary-exercise-do-or-not-attention-chart",
                title_text="Summary: Exercise (O or X) x Attention Score",
                description_text="운동을 했을 때와 안 했을 때의 집중도 평균의 차이",
                size=6,
            ),
            chart_card(
                "summary-exercise-do-or-not-happy-chart",
                title_text="Summary: Exercise (O or X) x Happy Score",
                description_text="운동을 했을 때와 안 했을 때의 행복도 평균의 차이",
                size=6,
            ),
        ])
    ], className="container-fluid")


def make_task_content(now):
    return html.Div([
        row_card([
            chart_card(
                "task-category-working-hour-monthly-chart",
                title_text="Task: Month x WorkingHour",
                description_text="카테고리 별 월간 작업시간의 누적 막대 그래프",
                size=6,
            ),
            chart_card(
                "task-working-hour-yearly-chart",
                title_text="Task: Month x WorkingHour",
                description_text="카테고리 별 월간 작업시간의 누적 막대 그래프",
                size=6,
                control_item=dcc.Dropdown(
                    id='year_dropdown',
                    options=[
                        {'label': '2017', 'value': '2017'},
                        {'label': '2018', 'value': '2018'},
                        {'label': '2019', 'value': '2019'},
                        {'label': '2020', 'value': '2020'},
                        {'label': '전체', 'value': '-1'},
                    ],
                    value='2017',
                    style={"width": "200px"},
                ),
            ),
        ]),
        row_card([
            html.Div([
                make_card_html([
                    dcc.Dropdown(
                        id='color-dropdown',
                        options=[
                            {'label': 'year', 'value': 'year'},
                            {'label': 'weekday', 'value': 'weekday'},
                            {'label': 'category', 'value': 'category'},
                        ],
                        value='year',
                    ),
                ], size=3, title_text="Color"),
                make_card_html([
                    dcc.RangeSlider(
                        id='task-start-hour-slider',
                        min=0,
                        max=26,
                        step=1,
                        value=[10, 19],
                        marks={
                            0: "0시",
                            3: "3시",
                            6: "6시",
                            10: '10시',
                            15: '오후 3시',
                            19: '오후 7시',
                            22: '오후 10시',
                        }
                    ),
                ], size= 9, title_text="StartHour"),
                make_card_html([
                    dcc.Checklist(
                        id='year-checklist',
                        options=[
                            {'label': '2017', 'value': '2017'},
                            {'label': '2018', 'value': '2018'},
                            {'label': '2019', 'value': '2019'},
                            {'label': '2020', 'value': '2020'},
                        ],
                        value=['2017'],
                    ),
                ], size=2, title_text="Year"),
                make_card_html([
                    dcc.Checklist(
                        id='weekday-checklist',
                        options=[{"label": list(calendar.day_name)[x], "value": list(calendar.day_name)[x]} for x in range(7)],
                        value=list(calendar.day_name)[:5],
                    ),
                ], size=3, title_text="Weekday"),
                make_card_html([
                    dcc.Checklist(
                        id='task-category-checklist',
                        options=[{"label": c, "value": c} for c in data_handler.TASK_CATEGORIES],
                        value=["Develop", "Research"],
                    ),
                ], size=7, title_text="Category"),
            ], className="container-fluid row"),
            chart_card("task-scatter-chart", size=8),
            chart_card("task-correlation-chart", size=4, title_text="작업에 대한 상관관계")
        ],
            title_text="Task: HappyScore x AttentionScore x WorkingHour x StartHour",
            description_text="각각의 작업에 대해서 어떠한 요소가 집중도에 가장 영향이 있는가",
        )
    ], className="container-fluid")


def make_sleep_content(now):
    return html.Div([
        html.H4("Metric:"),
        dcc.Dropdown(
            id='metric_dropdown',
            options=[
                {'label': 'Metric_v0', 'value': 'metric_v0'},
                {'label': 'Metric_v1', 'value': 'metric_v1'},
            ],
            value='metric_v0',
            style={"width": "200px"},
        ),
        chart_card(
            "sleep-hour-happy-scatter-chart",
            title_text="SleepTime x Happy",
            description_text="수면시간과 하루 행복도 점수 간의 상관관계",
            size=12,
        ),
        chart_card(
            "sleep-hour-attention-scatter-chart",
            title_text="SleepTime x Attention",
            description_text="수면시간과 하루 집중도 점수 간의 상관관계",
            size=12,
        ),
    ], className="container-fluid")
