# -*- coding: utf-8 -*-

import arrow
import calendar
import datetime
from dateutil import parser

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

import plotly.figure_factory as ff
import plotly.graph_objs as go

from data_handler import DataHandler

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

data_handler = DataHandler()


def get_sundays_of_this_month():
    WEEKDAY_SUNDAY = 6

    now = arrow.now()
    day_count = calendar.monthrange(now.year, now.month)[1]

    start_date = datetime.datetime(now.year, now.month, 1)
    end_date = datetime.datetime(now.year, now.month, day_count)

    sunday_dates = []
    for r in arrow.Arrow.range('day', start_date, end_date):
        if r.weekday() == WEEKDAY_SUNDAY:
            sunday_dates.append(r)
    return sunday_dates


def make_weekly_dates(N):
    format_date_list = []
    now = arrow.now()
    for i in range(-(N-1), 1, 1):
        date = now.replace(days=i)
        format_date_list.append(date.format("YYYY-MM-DD"))
    return format_date_list


app.layout = html.Div([
    html.Div(
        style={
            'height': '50px',
            'backgroundColor': '#438C59',
            'text-align': 'center'
        },
        children=html.Div([
            html.H5('Kino Dashboard', style={"color": "#fff", "padding-top": "8px"})
        ]),
        className='no-print'
    ),
    html.Div([
        html.Div([
            html.Div([
                dcc.Graph(id='live-daily-schedule'),
                dcc.Interval(
                    id='interval-component1',
                    interval=10*1000,  # every 10 secs
                    n_intervals=0
                )],
                className='ten columns',
                style={'margin-top': '20'},
            ),
            html.Div([
                dcc.Graph(id='live-weekly-reports'),
                dcc.Interval(
                    id='interval-component2',
                    interval=60*60*24*1000,  # every 1 day
                    n_intervals=0
                )],
                className='five columns',
                style={'margin-top': '20'},
            ),
            html.Div([
                dcc.Graph(id='live-daily-chart'),
                dcc.Interval(
                    id='interval-component3',
                    interval=60*60*24*1000,  # every 1 day
                    n_intervals=0
                )],
                className='five columns',
                style={'margin-top': '20'},
            ),
        ])
    ], className='columns printwidth100 noprintscroll')

])


# Multiple components can update everytime interval gets fired.
@app.callback(Output('live-daily-schedule', 'figure'),
              [Input('interval-component1', 'n_intervals')])
def make_daily_schedule_fig(n):
    today_record_data = data_handler.read_record()
    activity_data = today_record_data["activity"]
    task_data = activity_data["task"]

    toggl_projects = [data["project"] for data in task_data]
    colors = {}
    for data in task_data:
        colors[data["project"]] = data["color"]

    today_date = datetime.date.today().isoformat()
    tomorrow_date = (datetime.date.today() + datetime.timedelta(days=1)).isoformat()

    df = [  # Labeling scores
        dict(Task=5, Start=today_date, Finish=today_date, Resource=toggl_projects[0]),
        dict(Task=4, Start=today_date, Finish=today_date, Resource=toggl_projects[0]),
        dict(Task=3, Start=today_date, Finish=today_date, Resource=toggl_projects[0]),
        dict(Task=2, Start=today_date, Finish=today_date, Resource=toggl_projects[0]),
        dict(Task=1, Start=today_date, Finish=today_date, Resource=toggl_projects[0]),
    ]

    # Labeling projects
    for project in toggl_projects:
        df.append(
            dict(Task=1, Start=tomorrow_date, Finish=tomorrow_date, Resource=project)
        )

    for data in task_data:
        task = {
            "Task": data.get("score", 3),
            "Start": arrow.get(data["start_time"]).format("YYYY-MM-DD HH:mm:ss"),
            "Finish": arrow.get(data["end_time"]).format("YYYY-MM-DD HH:mm:ss"),
            "Resource": data["project"],
            "Description": data["description"],
        }
        df.append(task)

    fig = ff.create_gantt(df, colors=colors, index_col='Resource', title='Daily Schedule', group_tasks=True,
                        show_colorbar=True, bar_width=0.3, showgrid_x=True, showgrid_y=True, width=1200, height=600)

    happy_data = activity_data["happy"]

    if len(happy_data) > 0:
        xs = [arrow.get(d["time"]).format("YYYY-MM-DD HH:mm:ss") for d in happy_data]
        ys = [d["score"]-1 for d in happy_data]

        scatter_trace=dict(
            type='scatter',
            mode="markers",
            marker=dict(
                size=10,
                color="#439C59",
                line=dict(
                    width=2,
                ),
            ),
            name="Happy",
            x=xs,
            y=ys,
        )
        fig['data'].append(scatter_trace)

    # Annotations
    fig['layout']['annotations'] = []
    for index, d in enumerate(fig['data']):
        if len(d['x']) != 2:
            continue

        start_date, end_date = d['x']
        start_score, end_score = d['y']
        if start_date == end_date or start_score != end_score:
            continue

        description = d.get("text", "")
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

        up_ays = [-50, -90, -70, -110]
        down_ays = [50, 90, 70, 110]

        if start_score > 2:  # large than 3
            ays = up_ays
        else:
            ays = down_ays

        ay = ays[index % len(ays)]

        annotation = dict(
            x=start_date + (end_date - start_date) / 2,
            y=start_score,
            xref='x',
            yref='y',
            text=d.get("text", "None"),
            font=dict(
                family='Courier New, monospace',
                size=12,
                color='#fff'
            ),
            bgcolor=colors.get(project_name, "#DEDEDE"),
            bordercolor='#666',
            borderpad=2,
            arrowhead=7,
            ax=0,
            ay=ay,
            opacity=0.7,
        )
        fig['layout']['annotations'].append(annotation)

    return fig


# Multiple components can update everytime interval gets fired.
@app.callback(Output('live-weekly-reports', 'figure'),
              [Input('interval-component2', 'n_intervals')])
def make_stacked_bar_fig(n):
    categories = [
        "Article", "Blog", "Book", "Develop", "Exercise",
        "Hobby", "Management", "Meeting", "MOOC", "Planning",
        "Research", "Review", "Seminar", "Empty"
    ]
    task_reports = {}

    colors = {"Empty": "#DEDEDE"}
    dates = get_sundays_of_this_month()

    for c in categories:
        task_reports[c] = [0] * len(dates)

    for i in range(arrow.now().day, 0, -1):
        offset_day = i-1
        record_data = data_handler.read_record(days=-offset_day)

        curr_day = arrow.now().day - offset_day
        for task_index, sunday_date in enumerate(dates):
            if sunday_date.day - curr_day < 7 and sunday_date.day - curr_day >= 0:
                break

        activity_data = record_data.get("activity", {})
        task_data = activity_data.get("task", [])
        for t in task_data:
            project = t["project"]

            duration = (arrow.get(t["end_time"]) - arrow.get(t["start_time"])).seconds
            duration_hours = round(duration / 60 / 60, 1)

            task_reports[project][task_index] += duration_hours

            # Color
            if project not in colors:
                colors[project] = t["color"]

    data = []
    for category, task_report in task_reports.items():
        data.append(
            go.Bar(
                x=dates,
                y=task_report,
                name=category,
                marker=dict(
                    color=colors.get(category, "#DEDEDE"),
                    line=dict(
                        color='#222',
                        width=1,
                    ),
                ),
                opacity=0.8
            )
        )

    layout = go.Layout(
        autosize=True,
        barmode='stack',
        title="Weekly Task Report"
    )

    fig = go.Figure(data=data, layout=layout)
    return fig


# Multiple components can update everytime interval gets fired.
@app.callback(Output('live-daily-chart', 'figure'),
              [Input('interval-component3', 'n_intervals')])
def make_scatter_line_fig(n):
    week_days = 7

    weekly_data = []
    for i in range(week_days):
        record_data = data_handler.read_record(days=-i)
        weekly_data.append(record_data)

    dates = make_weekly_dates(week_days)

    def get_score(data, category):
        summary = data.get("summary", {})
        return summary.get(category, 0)

    attention_scores = [get_score(data, "attention") for data in weekly_data]
    happy_scores = [get_score(data, "happy") for data in weekly_data]
    productive_scores = [get_score(data, "productive") for data in weekly_data]
    sleep_scores = [get_score(data, "sleep") for data in weekly_data]
    repeat_task_scores = [get_score(data, "repeat_task") for data in weekly_data]
    total_scores = [get_score(data, "total") for data in weekly_data]

    names = ["attention", "happy", "productive", "sleep", "repeat_task", "total"]
    ys = [attention_scores, happy_scores, productive_scores, sleep_scores, repeat_task_scores, total_scores]

    # Create traces
    data = []
    for name, y in zip(names, ys):
        data.append(
            go.Scatter(
                x=dates,
                y=y,
                mode="lines+markers",
                name=name
            )
        )

    layout = go.Layout(
        autosize=True,
        title="Summary Chart"
    )

    fig = go.Figure(data=data, layout=layout)
    return fig


if __name__ == '__main__':
    app.run_server(debug=True, host="0.0.0.0", port=8000)
