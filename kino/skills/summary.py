
import arrow

import skills
import slack
from slack import MsgResource
import utils

class Summary(object):

    def __init__(self):
        pass

    def total_score(self):
        slackbot = slack.SlackerAdapter()
        template = slack.MsgTemplate()

        today_data = self.__total_score("today")
        color = MsgResource.SCORE_COLOR(today_data['Total'])

        yesterday_data = self.__total_score("yesterday")
        for k,v in today_data.items():
            if type(v) == float:
                diff = v - yesterday_data.get(k, False)
                if not diff:
                    continue
                else:
                    diff = round(diff*100)/100

                if diff > 0:
                    diff = "+" + str(diff)
                else:
                    diff = str(diff)
                today_data[k] = str(v) + " (" + diff + ")"

        today_data['Color'] = color
        attachments = template.make_summary_template(today_data)
        slackbot.send_message(attachments=attachments)

    def __total_score(self, timely):
        if timely == "today":
            productive = self.__productive_score()
            happy = self.__happy_score()

            today_data = self.__get_data("today")
            diary = today_data.get('diary', False)
            exercise = today_data.get('exercise', False)

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
            return self.__get_data("yesterday")


    def __productive_score(self):
        rescue_time_point = skills.RescueTime().get_point()
        toggl_point = skills.TogglManager().get_point()
        github_point = skills.GithubManager().get_point()
        todoist_point = skills.TodoistManager().get_point()
        return (rescue_time_point + github_point + todoist_point + toggl_point)

    def __happy_score(self):
        happy_data = skills.Happy().get_data()
        return sum(list(map(lambda x: int(x), happy_data.values()))) / len(happy_data)

    def __get_data(self, timely):
        data_handler = utils.DataHandler()
        if timely == "today":
            date = arrow.now()
        elif timely == "yesterday":
            date = arrow.now().replace(days=-1)
        fname = "summary/" + date.format('YYYY-MM-DD') + ".json"
        return data_handler.read_file(fname)

    def __write_data(self, data):
        data_handler = utils.DataHandler()
        fname = "summary/" + arrow.now().format('YYYY-MM-DD') + ".json"
        return data_handler.write_file(fname, data)

    def do_write_diary(self):
        today_data = self.__get_data("today")
        today_data['diary'] = True
        self.__write_data(today_data)

    def do_exercise(self):
        today_data = self.__get_data("today")
        today_data['exercise'] = True
        self.__write_data(today_data)
