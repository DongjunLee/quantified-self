
import arrow

import skills
import slack
from slack import MsgResource
import utils

class Summary(object):

    def __init__(self):
        self.data_handler = utils.DataHandler()
        self.slackbot = slack.SlackerAdapter()

    def total_score(self):
        template = slack.MsgTemplate()

        today_data = self.__get_total_score()
        self.data_handler.edit_record(today_data)

        color = MsgResource.SCORE_COLOR(today_data['Total'])
        today_data['Color'] = color

        yesterday_data = self.__get_total_score(-1)
        for k,v in today_data.items():
            if type(v) == float:
                y_point = yesterday_data.get(k, False)
                if not y_point:
                    continue
                else:
                    diff = v - y_point
                    diff = round(diff*100)/100

                if diff > 0:
                    diff = "+" + str(diff)
                else:
                    diff = str(diff)
                today_data[k] = str(v) + " (" + diff + ")"
            elif type(v) == bool:
                if v:
                    today_data[k] = "O"
                else:
                    today_data[k] = "X"

        record = self.data_handler.read_record()
        good_morning = arrow.get(record['GoodMorning'])
        now = arrow.now()
        activity_time = (now - good_morning).seconds / 60 / 60
        activity_time = round(activity_time*100)/100
        today_data['Activity Time'] = good_morning.format("HH:mm") + " ~ " + now.format("HH:mm") + " : " + str(activity_time) + "h"

        attachments = template.make_summary_template(today_data)
        self.slackbot.send_message(attachments=attachments)

    def __get_total_score(self, days="today"):
        if days == "today":
            productive = self.__productive_score()
            happy = self.__happy_score()

            today_data = self.data_handler.read_record()
            diary = today_data.get('Diary', False)
            exercise = today_data.get('Exercise', False)

            score = utils.Score()
            total = score.percent(happy, 50, 100) + score.percent(productive, 40, 100)
            if diary:
                total += 5
            if exercise:
                total += 5

            data = {
                "Productive": round(productive*100)/100,
                "Happy": round(happy*100)/100,
                "Diary": diary,
                "Exercise": exercise,
                "Total": round(total*100)/100
            }
            return data
        elif type(days) == int:
            return self.data_handler.read_record(days=days)

    def __productive_score(self):
        rescue_time_point = skills.RescueTime().get_point()
        toggl_point = skills.TogglManager().get_point()
        github_point = skills.GithubManager().get_point()
        todoist_point = skills.TodoistManager().get_point()

        data = {
            "rescue_time": round(rescue_time_point*100)/100,
            "toggl": round(toggl_point*100)/100,
            "github": round(github_point*100)/100,
            "todoist": round(todoist_point*100)/100
        }
        self.data_handler.edit_record(('productive', data))

        score = utils.Score()
        rescue_time_point = score.percent(rescue_time_point, 10, 100)
        github_point = score.percent(github_point, 10, 100)
        todoist_point = score.percent(todoist_point, 30, 100)
        toggl_point = score.percent(toggl_point, 50, 100)
        return (rescue_time_point + github_point + todoist_point + toggl_point)

    def __happy_score(self):
        happy_data = self.data_handler.read_record().get('happy', {})
        if len(happy_data) > 0:
            return sum(list(map(lambda x: int(x), happy_data.values()))) / len(happy_data)
        else:
            return 0

    def record_write_diary(self):
        self.data_handler.edit_record(('Diary', True))

    def record_exercise(self):
        self.data_handler.edit_record(('Exercise', True))

    def record_good_morning(self):
        now = arrow.now()
        self.data_handler.edit_record(('GoodMorning', str(now)))

    def record_good_night(self):
        now = arrow.now()
        self.data_handler.edit_record(('GoodNight', str(now)))

    def total_chart(self):
        records = []
        for i in range(-6, 1, 1):
            records.append(self.__get_total_score(i))

        date = [-6, -5, -4, -3, -2, -1, 0]
        x_ticks = ['6 day before', '5 day before', '4 day before', '3 day before', '2 day before', 'yesterday', 'today']
        legend = ['Happy', 'Productive', 'Total']
        data = []
        for l in legend:
            data.append(list(map(lambda x: x[l], records)))

        f_name = "total_weekly_report.png"
        title = "Total Report"

        plot = slack.Plot
        plot.make_line(date, data, f_name, legend=legend, x_ticks=x_ticks,
                            x_label="Total Point", y_label="Days", title=title)
        self.slackbot.file_upload(f_name, title=title, comment=MsgResource.TOTAL_REPORT)
