#coding: UTF-8

import asyncio
import datetime
import os
import websockets

from github import Github
from slacker import Slacker

SLACK_TOKEN = os.environ["STALKER_BOT_TOKEN"]
slack = Slacker(SLACK_TOKEN)

# Send a message to #general channel
slack.chat.post_message(channel='#bot_test', text='Hello fellow slackers!', as_user=True)

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
    slack.chat.post_message(channel="#bot_test", text="Github No Commit!", as_user=True)
else:
    text = "Github " + str(len(commit_events)) + " commits!!"
    slack.chat.post_message(channel="#bot_test", text=text, as_user=True)


# Start Bot

response = slack.rtm.start()
endpoint = response.body['url']

async def execute_bot():
    ws = await websockets.connect(endpoint)
    while True:
        message_json = await ws.recv()
        print(message_json)

loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)
asyncio.get_event_loop().run_until_complete(execute_bot())
asyncio.get_event_loop().run_forever()


