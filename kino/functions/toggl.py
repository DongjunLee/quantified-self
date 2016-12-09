
import arrow
from toggl import Toggl

import slack
from slack import MsgResource
import utils

class TogglManager(object):

    def __init__(self):
        self.config = utils.Config()
        self.slackbot = slack.SlackerAdapter()

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
        if current_timer is None:
            return

        diff_min = self.__get_curr_time_diff(start=current_timer['start'])
        diff_min_divide_10 = int(diff_min/10)
        if diff_min > 100:
            self.slackbot.send_message(text=MsgResource.TOGGL_NOTI_RELAY)
        elif diff_min_divide_10 == 3:
            self.slackbot.send_message(text=MsgResource.TOGGL_TIMER_CHECK(diff_min))
        elif diff_min_divide_10== 6:
            self.slackbot.send_message(text=MsgResource.TOGGL_TIMER_CHECK(diff_min))
        elif diff_min_divide_10 == 9:
            self.slackbot.send_message(text=MsgResource.TOGGL_TIMER_CHECK(diff_min))

    def __get_curr_time_diff(self, start=None, stop=arrow.utcnow()):
        if type(start) is str:
            start = arrow.get(start)
        if type(stop) is str:
            stop = arrow.get(stop)

        diff = (stop - start).seconds / 60
        return int(diff)

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
