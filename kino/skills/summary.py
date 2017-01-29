
import arrow

import skills
import slack
from slack import MsgResource
import utils

class Summary(object):

    def __init__(self):
        self.data_handler = utils.DataHandler()

    def total_score(self):
        slackbot = slack.SlackerAdapter()
        template = slack.MsgTemplate()

        today_data = self.__total_score("today")
        color = MsgResource.SCORE_COLOR(today_data['Total'])

        self.data_handler.edit_record(today_data)

        yesterday_data = self.__total_score("yesterday")
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

        today_data['Color'] = color
        attachments = template.make_summary_template(today_data)
        slackbot.send_message(attachments=attachments)

    def __total_score(self, timely):
        if timely == "today":
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
        elif timely == "yesterday":
            return self.data_handler.read_record(days=-1)

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

    def do_write_diary(self):
        self.data_handler.edit_record(('Diary', True))

    def do_exercise(self):
        self.data_handler.edit_record(('Exercise', True))
