
import arrow

import nlp
import skills
import slack
from slack import MsgResource
import utils

class Summary(object):

    def __init__(self):
        self.data_handler = utils.DataHandler()
        self.slackbot = slack.SlackerAdapter()
        self.profile = utils.Profile()

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
                    diff = v - float(y_point)
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
        activity = record.get('activity', {})

        arrow_util = utils.ArrowUtil()

        # Sleep Time
        go_to_bed = activity.get('go_to_bed', None)
        wake_up = activity.get('wake_up', None)

        if (go_to_bed is not None and wake_up is not None):
            go_to_bed_time = arrow.get(go_to_bed)
            wake_up_time = arrow.get(wake_up)

            sleep_hour = arrow_util.get_curr_time_diff(start=go_to_bed_time, stop=wake_up_time, base_hour=True)
            today_data['Sleep'] = go_to_bed_time.format("HH:mm") + " ~ " + wake_up_time.format("HH:mm") + " : " + str(sleep_hour) + "h (" + str(today_data['Sleep']) + ")"

        # Working Hour
        in_company = activity.get('in_company', None)
        out_company = activity.get('out_company', None)

        if (in_company is not None and out_company is not None):
            in_company_time = arrow.get(in_company)
            out_company_time = arrow.get(out_company)

            working_hour = arrow_util.get_curr_time_diff(start=in_company_time, stop=out_company_time, base_hour=True)
            today_data['Working Hour'] = in_company_time.format("HH:mm") + " ~ " + out_company_time.format("HH:mm") + " : " + str(working_hour) + "h"

        attachments = template.make_summary_template(today_data)
        self.slackbot.send_message(attachments=attachments)

    def __get_total_score(self, days="today"):
        if days == "today":
            productive = self.__productive_score()
            happy = self.__happy_score()
            sleep = self.__sleep_score()
            repeat = self.__repeat_task_score()

            today_data = self.data_handler.read_record()
            diary = today_data.get('Diary', False)
            exercise = today_data.get('Exercise', False)
            bat = today_data.get('BAT', False)

            score = utils.Score()
            total = (score.percent(happy, self.profile.get_score('HAPPY'), 100)
                      + score.percent(productive, self.profile.get_score('PRODUCTIVE'), 100)
                      + score.percent(sleep, self.profile.get_score('SLEEP'), 100)
                      + repeat)

            if diary:
                total += self.profile.get_score('DIARY')
            if exercise:
                total += self.profile.get_score('EXERCISE')
            if bat:
                total += self.profile.get_score('BAT')

            data = {
                "Productive": round(productive*100)/100,
                "Happy": round(happy*100)/100,
                "Sleep": round(sleep*100)/100,
                "Diary": diary,
                "Exercise": exercise,
                "Total": round(total*100)/100
            }
            return data
        elif type(days) == int:
            data = self.data_handler.read_record(days=days)
            column_list = ["Productive", "Happy", "Sleep", "Total"]
            for c in column_list:
                if c not in data:
                    data[c] = 0
            return data

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

        base_point = 0
        rescue_time_ratio = self.profile.get_score('productives')['RESCUE_TIME']
        github_ratio = self.profile.get_score('productives')['GITHUB']
        todoist_ratio = self.profile.get_score('productives')['TODOIST']
        toggl_ratio = self.profile.get_score('productives')['TOGGL']

        if self.is_holiday():
            base_point = self.profile.get_score('HOLIDAY_BASE')
            holiday_ratio = self.profile.get_score('HOLIDAY_RATIO')

            rescue_time_ratio *= holiday_ratio
            github_ratio *= holiday_ratio
            todoist_ratio *= holiday_ratio
            toggl_ratio *= holiday_ratio

        rescue_time_point = score.percent(rescue_time_point, rescue_time_ratio, 100)
        github_point = score.percent(github_point, github_ratio, 100)
        todoist_point = score.percent(todoist_point, todoist_ratio, 100)
        toggl_point = score.percent(toggl_point, toggl_ratio, 100)
        return (base_point + rescue_time_point + github_point + todoist_point + toggl_point)

    def __happy_score(self):
        happy_data = self.data_handler.read_record().get('happy', {})
        if len(happy_data) > 0:
            return sum(list(map(lambda x: int(x), happy_data.values()))) / len(happy_data)
        else:
            return 0

    def __sleep_score(self):
        activity_data = self.data_handler.read_record().get('activity', {})

        go_to_bed_time = arrow.get(activity_data.get('go_to_bed', None))
        wake_up_time = arrow.get(activity_data.get('wake_up', None))

        sleep_time = (wake_up_time - go_to_bed_time).seconds / 60 / 60
        sleep_time = sleep_time*100

        if sleep_time > 800:
            sleep_time -= (sleep_time - 800)

        if sleep_time > 700:
            sleep_time = 700

        score = utils.Score()
        return score.percent(sleep_time, 100, 700)

    def __repeat_task_score(self):
        todoist = skills.TodoistManager()
        minus_point = 2.5
        if self.is_holiday():
            minus_point /= 2
        return 10 - (minus_point * todoist.get_repeat_task_count())

    def record_write_diary(self):
        self.data_handler.edit_record(('Diary', True))

    def record_exercise(self):
        self.data_handler.edit_record(('Exercise', True))

    def record_holiday(self, dnd):
        self.data_handler.edit_record(('Holiday', dnd))

    def is_holiday(self):
        record = self.data_handler.read_record()
        holiday = record.get('Holiday', None)
        if holiday is None:
            arrow_util = utils.ArrowUtil()
            return not arrow_util.is_weekday()
        else:
            return holiday

    def check_go_to_bed(self):
        state = nlp.State()
        state.check()
        presence_log = state.current[state.SLEEP]
        if presence_log['presence'] == 'away':
            go_to_bed_time = arrow.get(presence_log['time'])
            self.data_handler.edit_record_with_category('activity', ('go_to_bed', str(go_to_bed_time)))

    def total_chart(self):
        records = []
        for i in range(-6, 1, 1):
            records.append(self.__get_total_score(i))

        date = [-6, -5, -4, -3, -2, -1, 0]
        x_ticks = ['6 day before', '5 day before', '4 day before', '3 day before', '2 day before', 'yesterday', 'today']
        legend = ['Happy', 'Productive', 'Sleep', 'Total']
        data = []
        for l in legend:
            data.append(list(map(lambda x: x[l], records)))

        f_name = "total_weekly_report.png"
        title = "Total Report"

        plot = slack.Plot
        plot.make_line(date, data, f_name, legend=legend, x_ticks=x_ticks,
                            x_label="Total Point", y_label="Days", title=title)
        self.slackbot.file_upload(f_name, title=title, comment=MsgResource.TOTAL_REPORT)
