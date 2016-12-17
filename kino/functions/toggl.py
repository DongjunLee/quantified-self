
import arrow
from toggl import Toggl

import slack
from slack import MsgResource
import utils

class TogglManager(object):

    def __init__(self):
        self.config = utils.Config()
        self.slackbot = slack.SlackerAdapter()
        self.logger = utils.Logger().get_logger()

        self.toggl = Toggl()
        self.toggl.setAPIKey(self.config.toggl['TOKEN'])

        wid = self.toggl.getWorkspace(name=self.config.toggl['WORKSPACE_NAME'])['id']
        self.toggl.setWorkspaceId(wid)

        self.entity = TogglProjectEntity().entity

    def timer(self, description=None):
        current_timer = self.toggl.currentRunningTimeEntry()['data']
        if current_timer is None:
            if description is None or description == "":
                pid = None
            else:
                # matching name
                lower_description = description.lower()
                name = None
                for key, value_list in self.entity['project'].items():
                    if any(v in lower_description for v in value_list):
                        name = key
                        pid = self.__get_pid(name=name)
                    else:
                        pid = None

            self.toggl.startTimeEntry(description=description, pid=pid)
            self.slackbot.send_message(text=MsgResource.TOGGL_START)
        else:
            stop = self.toggl.stopTimeEntry(current_timer['id'])
            description = stop['data'].get('description', 'no description')
            diff_min = self.__get_curr_time_diff(start=stop['data']['start'], stop=stop['data']['stop'])

            self.slackbot.send_message(text=MsgResource.TOGGL_STOP)
            self.slackbot.send_message(text=MsgResource.TOGGL_STOP_SUMMARY(description, diff_min))

    def __get_pid(self, name=None):
        project = self.toggl.getWorkspaceProject(name=name)
        if project == None:
            pid = None
        else:
            pid = project['id']
        return pid

    def check_toggl_timer(self):
        current_timer = self.toggl.currentRunningTimeEntry()['data']
        self.logger.info(str(current_timer))
        if current_timer is None:
            return

        diff_min = self.__get_curr_time_diff(start=current_timer['start'])
        self.logger.info("diff_min: " + str(diff_min))
        diff_min_divide_10 = int(diff_min/10)
        if diff_min > 100:
            self.slackbot.send_message(text=MsgResource.TOGGL_NOTI_RELAY)
        else:
            for i in range(3, 10, 3):
                if diff_min_divide_10 == i:
                    self.slackbot.send_message(text=MsgResource.TOGGL_TIMER_CHECK(diff_min))
                    break

    def __get_curr_time_diff(self, start=None, stop=None):
        if type(start) is str:
            start = arrow.get(start)
        if type(stop) is str:
            stop = arrow.get(stop)

        if stop is None:
            stop = arrow.utcnow()

        self.logger.info(str(stop))

        diff = (stop - start).seconds / 60
        return int(diff)

    def report(self, kind="chart", timely="weekly"):

        now = arrow.now()

        if timely == "daily":
            before_days = now.replace(days=0)
        elif timely == "weekly":
            before_days = now.replace(days=-6)

        data = {
            'since': before_days.format('YYYY-MM-DD'),
            'until': now.format('YYYY-MM-DD'),
            'calculate': 'time'
        }

        if kind == "basic":
            f_name = "basic-report.pdf"
            self.toggl.getWeeklyReportPDF(data, f_name)
            self.slackbot.file_upload(f_name, title=timely + " 기본 리포트", comment=MsgResource.TOGGL_REPORT)
        elif kind == "chart":
            f_name = "chart-report.pdf"
            self.toggl.getSummaryReportPDF(data, f_name)
            self.slackbot.file_upload(f_name, title=timely + " 차트 리포트", comment=MsgResource.TOGGL_REPORT)
        elif kind == "detail":
            f_name = "detail-report.pdf"
            self.toggl.getDetailedReportPDF(data, f_name)
            self.slackbot.file_upload(f_name, title=timely + " 상세 리포트", comment=MsgResource.TOGGL_REPORT)

class TogglProjectEntity(object):
    class __Entity:
        def __init__(self):
            self.entity = utils.DataHandler().read_file("toggl.json")

    instance = None
    def __init__(self):
        if not TogglProjectEntity.instance:
            TogglProjectEntity.instance = TogglProjectEntity.__Entity()

    def __getattr__(self, name):
        return getattr(self.instance, name)
