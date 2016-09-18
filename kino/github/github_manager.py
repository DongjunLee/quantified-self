import datetime
import os

from github import Github

# Github

today = datetime.datetime.today()
today_date = datetime.datetime(today.year, today.month, today.day)
today_date_ko = today_date - datetime.timedelta(hours=9)

username = os.environ["GITHUB_USERNAME"]
password = os.environ["GITHUB_PASSWORD"]

client = Github(username, password)

commit_events = []

for event in client.get_user(username).get_events():
    if event.created_at > today_date_ko:
        if event.type in ['PushEvent', 'PullRequestEvent']:
            commit_events.append(event)
    else:
        break

if len(commit_events) == 0:
    # push message to slack
    pass
else:
    text = "Github " + str(len(commit_events)) + " commits!!"
    pass

