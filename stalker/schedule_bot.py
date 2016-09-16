#coding: UTF-8

import datetime
import os
import schedule
import threading
import time

from github import Github
from slacker import Slacker

SLACK_TOKEN = os.environ["STALKER_BOT_TOKEN"]
slack = Slacker(SLACK_TOKEN)

# Send a message to #general channel
slack.chat.post_message(channel='#bot_test', text='Hello fellow slackers!', as_user=True)

# Schedule
def job():
    msg = ("I'm running on thread %s" % threading.current_thread())
    slack.chat.post_message(channel="#bot_test", text=msg, as_user=True)

def run_threaded(job_func):
    job_thread = threading.Thread(target=job_func)
    job_thread.start()

schedule.every(10).seconds.do(run_threaded, job)

while True:
    schedule.run_pending()
    time.sleep(1)
