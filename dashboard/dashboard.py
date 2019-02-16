# -*- coding: utf-8 -*-

import arrow
import datetime
from dateutil import parser

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

import numpy as np

import plotly.figure_factory as ff
import plotly.graph_objs as go

from data_handler import DataHandler

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

data_handler = DataHandler()


def make_stacked_bar_fig():

    dates = [
        datetime.datetime(2019, 1, 1),
        datetime.datetime(2019, 1, 8),
        datetime.datetime(2019, 1, 15),
        datetime.datetime(2019, 1, 22),
        datetime.datetime(2019, 1, 29)]
    categories = ["Article", "Blog", "Book", "Develop", "Exercise", "Hobby", "Meeting", "MOOC", "Planning", "Research", "Review", "Seminar"]

    data = []
    for c in categories:
        data.append(
            go.Bar(
                x=dates,
                y=[1, 2, 3, 4, 5],
                name=c
            )
        )

    layout = go.Layout(
        autosize=True,
        barmode='stack',
        title="Weekly Task Report"
    )

    fig = go.Figure(data=data, layout=layout)
    return fig


def make_scatter_line_fig():
    N = 5
    dates = [datetime.datetime(2019, 1, 1),
             datetime.datetime(2019, 1, 8),
             datetime.datetime(2019, 1, 15),
             datetime.datetime(2019, 1, 22),
             datetime.datetime(2019, 1, 29)]
    random_y0 = np.random.randn(N) + 5
    random_y1 = np.random.randn(N) + 7
    random_y2 = np.random.randn(N) + 10

    ys = [random_y0, random_y1, random_y2]

    # Create traces
    data = []
    for index, y in enumerate(ys):
        data.append(
            go.Scatter(
                x=dates,
                y=y,
                mode="lines+markers",
                name=index
            )
        )

    layout = go.Layout(
        autosize=True,
        title="Summary Chart"
    )

    fig = go.Figure(data=data, layout=layout)
    return fig


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
                    id='interval-component',
                    interval=10*1000,  # every 10 secs
                    n_intervals=0
                )],
                className='ten columns',
                style={'margin-top': '20'},
            ),
            html.Div([
                dcc.Graph(
                    id='example-graph2',
                    figure=make_stacked_bar_fig()
                )],
                className='five columns',
                style={'margin-top': '20'}
            ),
            html.Div([
                dcc.Graph(
                    id='example-graph3',
                    figure=make_scatter_line_fig()
                )],
                className='five columns',
                style={'margin-top': '20'}
            )
        ])
    ], className='columns printwidth100 noprintscroll')

])


# Multiple components can update everytime interval gets fired.
@app.callback(Output('live-daily-schedule', 'figure'),
              [Input('interval-component', 'n_intervals')])
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
        ys = [d["score"] for d in happy_data]

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


if __name__ == '__main__':
    app.run_server(debug=True, host="0.0.0.0", port=8000)
