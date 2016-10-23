
from dateutil.parser import parse
from pytz import timezone
import todoist

from kino.template import MsgTemplate
from slack.slackbot import SlackerAdapter
from utils.config import Config
from utils.resource import MessageResource

class TodoistManager(object):

    def __init__(self):
        self.config = Config()
        self.todoist_api = todoist.TodoistAPI(self.config.todoist['TOKEN'])
        self.slackbot = SlackerAdapter()
        self.template = MsgTemplate()

    def today_briefing(self, channel=None):
        self.slackbot.send_message(text=MessageResource.TODOIST_TODAY_BREIFING, channel=channel)

        overdue_task_count = self.__get_overdue_task_count()
        today_task = self.__get_today_task()
        today_task_count = len(today_task)

        task_text = MessageResource.TODOIST_OVERDUE(overdue_task_count) + "\n" + MessageResource.TODOIST_TODAY(today_task_count)
        self.slackbot.send_message(text=task_text, channel=channel)

        specific_task_list = self.__get_specific_time_task(today_task)
        attachments = self.template.make_todoist_task_template(specific_task_list)
        self.slackbot.send_message(attachments=attachments, channel=channel)

        karma_trend = self.__get_karma_trend()
        karma_trend_text = MessageResource.TODOIST_KARMA(karma_trend)
        self.slackbot.send_message(text=karma_trend_text, channel=channel)

    def __get_overdue_task_count(self):
        overdue_task_count = 0
        # 7 day ~ 1 day before
        for i in range(7,0,-1):
            query = str(i) + ' day before'
            before = self.todoist_api.query([query])[0]['data']
            overdue_task_count += len(before)
        return overdue_task_count

    def __get_today_task(self):
        return self.todoist_api.query(['today'])[0]['data']

    def __get_specific_time_task(self, today_task):
        specific_task_list = []
        for t in today_task:
            if ':' in t['date_string'] or '분' in t['date_string']:
                due_time = parse(t['due_date']).astimezone(timezone('Asia/Seoul'))
                due_time = due_time.strftime("%H:%M")

                project_name = self.todoist_api.projects.get_by_id(t['project_id'])
                project_name = project_name.data['name']

                specific_task_list.append( (project_name, t['content'], due_time, t['priority']) )
        return specific_task_list

    def __get_karma_trend(self):
        user = self.todoist_api.user.login(self.config.todoist['ID'], self.config.todoist['PASSWORD'])
        return user['karma_trend']

    def today_summary(self, channel=None):
        self.slackbot.send_message(text=MessageResource.TODOIST_TODAY_SUMMARY, channel=channel)

        overdue_task_count = self.__get_overdue_task_count()
        today_task = self.__get_today_task()
        today_task_count = len(today_task)

        overdue_today_text = MessageResource.TODOIST_SUMMARY_OVERDUE(overdue_task_count+today_task_count)
        self.slackbot.send_message(text=overdue_today_text, channel=channel)

        added_count, completed_count, updated_count = self.__get_event_counts()
        event_text = MessageResource.TODOIST_SUMMARY_EVENT(added_count, completed_count, updated_count)
        self.slackbot.send_message(text=event_text, channel=channel)

    def __get_event_counts(self):
        activity_log_list = self.todoist_api.activity.get()
        added_task_count = 0
        completed_task_count = 0
        updated_task_count = 0
        for log in activity_log_list:
            event_type = log['event_type']
            if event_type == 'added':
                added_task_count += 1
            elif event_type == 'completed':
                completed_task_count += 1
            elif event_type == 'updated':
                updated_task_count += 1
        return added_task_count, completed_task_count, updated_task_count
