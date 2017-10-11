
from hbconfig import Config
import jenkins

from ..slack.resource import MsgResource
from ..slack.slackbot import SlackerAdapter



class JenkinsClient:

    def __init__(self, slackbot=None):
        config = Config()
        self.api = jenkins.Jenkins(
            config.open_api.jenkins.URL,
            username=config.open_api.jenkins.USERNAME,
            password=config.open_api.jenkins.PASSWORD)
        self.token = config.open_api.jenkins.TOKEN

        if slackbot is None:
            self.slackbot = SlackerAdapter()
        else:
            self.slackbot = slackbot

    def build(self, name: str, branch: str):

        if name is None or branch is None:
            self.slackbot.send_message(text=MsgResource.JENKINS_JOB_NOT_UNDERSTAND)
            return

        job = self.get_job(name, branch)

        if job is None:
            self.slackbot.send_message(text=MsgResource.JENKINS_JOB_NOT_UNDERSTAND)
        else:
            self.slackbot.send_message(text=MsgResource.JENKINS_BUILD_START)
            self.api.build_job(job["name"], parameters={}, token=self.token)

    def get_job(self, name: str, branch: str):
        jobs = self.api.get_jobs()
        job = next(filter(lambda j: name in j["name"] and branch in j["name"], jobs))
        return job
