# -*- coding: utf-8 -*-

import arrow
import datetime
from dateutil import parser

import dash
import dash_core_components as dcc
import dash_html_components as html

import numpy as np

import plotly.figure_factory as ff
import plotly.graph_objs as go

from data_handler import DataHandler

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

data_handler = DataHandler()


def make_daily_schedule_fig(activity_data):
    task_data = activity_data["task"]
    # toggl_projects = ["Article", "Blog", "Book", "Develop", "Exercise", "Hobby", "Meeting", "MOOC", "Planning", "Research", "Review", "Seminar"]

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

    # dict(Task='<score>', Start=f'{today_date}', Finish=f'{today_date} 6:00:00', Resource='<project>', Description='<description>'),

    # tasks = [
        # dict(Task='1', Start=f'{today_date}', Finish=f'{today_date} 6:00:00', Resource='Article', Description="Test"),
        # dict(Task='1', Start=f'{today_date} 7:00:00', Finish=f'{today_date} 7:30:00', Resource='Blog', Description="Seminar"),
        # dict(Task='2', Start=f'{today_date} 9:00:00', Finish=f'{today_date} 11:25:00', Resource='Develop', Description="Develop"),
        # dict(Task='3', Start=f'{today_date} 11:30:00', Finish=f'{today_date} 12:00:00', Resource='Hobby', Description="reasoning-qa"),
        # dict(Task='4', Start=f'{today_date} 12:00:00', Finish=f'{today_date} 13:00:00', Resource='Develop'),
        # dict(Task='5', Start=f'{today_date} 13:00:00', Finish=f'{today_date} 17:00:00', Resource='Meeting'),
        # dict(Task='3', Start=f'{today_date} 17:30:00', Finish=f'{today_date} 18:30:00', Resource='MOOC'),
        # dict(Task='5', Start=f'{today_date} 18:30:00', Finish=f'{today_date} 19:00:00', Resource='Research'),
        # dict(Task='3', Start=f'{today_date} 19:00:00', Finish=f'{today_date} 20:00:00', Resource='Seminar'),
        # dict(Task='4', Start=f'{today_date} 21:00:00', Finish=f'{today_date} 23:59:00', Resource='Review')
    # ]

    for data in task_data:
        task = {
            "Task": data.get("score", 3),
            "Start": arrow.get(data["start_time"]).format("YYYY-MM-DD HH:mm:ss"),
            "Finish": arrow.get(data["end_time"]).format("YYYY-MM-DD HH:mm:ss"),
            "Resource": data["project"],
            "Description": data["description"],
        }
        df.append(task)

    # colors = dict(
        # Article = 'rgb(46, 137, 205)',
        # Blog = 'rgb(114, 44, 121)',
        # Book = 'rgb(198, 47, 105)',
        # Develop = 'rgb(58, 149, 136)',
        # Exercise = 'rgb(107, 127, 135)',
        # Hobby = 'rgb(107, 127, 135)',
        # Meeting = 'rgb(107, 127, 135)',
        # MOOC = 'rgb(107, 127, 135)',
        # Planning = 'rgb(107, 127, 135)',
        # Research = '#222',
        # Review = 'rgb(107, 127, 135)',
        # Seminar = 'rgb(107, 127, 135)',
    # )

    fig = ff.create_gantt(df, colors=colors, index_col='Resource', title='Daily Schedule', group_tasks=True,
                        show_colorbar=True, bar_width=0.5, showgrid_x=True, showgrid_y=True, width=1200, height=600)

    # scatter_trace=dict(
        # type='scatter',
        # name="Happy",
        # x=[datetime.datetime(2019, 2, 5, 9, 00), datetime.datetime(2019, 2, 5, 10, 00)],
        # y=[1, 3]
    # )
    # fig['data'].append(scatter_trace)

    # Annotations
    fig['layout']['annotations'] = []
    for index, d in enumerate(fig['data']):
        start_date, end_date = d['x']
        start_score, end_score = d['y']

        if start_date == end_date or start_score != end_score:
            continue

        if type(start_date) != datetime.datetime:
            start_date = parser.parse(start_date)
        if type(end_date) != datetime.datetime:
            end_date = parser.parse(end_date)

        ays = [50, -50, 70, -70, 90, -90]
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
                color='#222'
            ),
            bgcolor='#fff',
            bordercolor='#222',
            borderpad=4,
            arrowhead=7,
            ax=0,
            ay=ay,
        )
        fig['layout']['annotations'].append(annotation)

    return fig


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


today_recode_data = data_handler.read_record()

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
                dcc.Graph(
                    id='example-graph1',
                    figure=make_daily_schedule_fig(today_recode_data["activity"])
                )],
                className='ten columns',
                style={'margin-top': '20'}
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

if __name__ == '__main__':
    app.run_server(debug=True)
