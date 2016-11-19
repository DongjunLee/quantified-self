
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
        # matching name
        lower_description = description.lower()
        name = None
        for key, value_list in self.entity['project'].items():
            if any(v in lower_description for v in value_list):
                name = key
        pid = self.__get_pid(name=name)

        current_timer = self.toggl.currentRunningTimeEntry()['data']
        if current_timer is None:
            self.toggl.startTimeEntry(description=description, pid=pid)

            self.slackbot.send_message(text=MsgResource.TOGGL_START)
        else:
            stop = self.toggl.stopTimeEntry(current_timer['id'])
            description = stop['data']['description']
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

    def notify_need_relax(self):
        current_timer = self.toggl.currentRunningTimeEntry()
        diff_min = self.__get_curr_time_diff(start=current_timer['data']['start'])
        if diff_min > 90:
            self.slackbot.send_message(text=MsgResource.TOGGL_NOTI_RELAY)

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
