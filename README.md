<p align="center">
  <img src="images/kino-title.png" style="inline" width=250>
</p>

<h3 align="center">
  <sup><strong>
    Personal Assistant Based on Slack Bot for Myself
  </strong></sup>
</h3>


<p align="center">
 
  <a href="https://travis-ci.org/badges/shields">
    <img src="https://travis-ci.org/DongjunLee/kino-bot.svg?branch=master" alt="build status">
  </a>
  
  <a href="https://codecov.io/gh/DongjunLee/kino-bot">
    <img src="https://codecov.io/gh/DongjunLee/kino-bot/branch/develop/graph/badge.svg" alt="Codecov" />
  </a>
  
  <a href="https://github.com/ambv/black">
    <img src="https://img.shields.io/badge/code%20style-black-000000.svg" alt="Code Style">
  </a>
  
  <br/>
  
  <a href="https://requires.io/github/DongjunLee/kino-bot/requirements/?branch=master">
    <img src="https://requires.io/github/DongjunLee/kino-bot/requirements.svg?branch=master" alt="Requirements Status" />
  </a>
  
  <a href='https://dependencyci.com/github/DongjunLee/kino-bot'>
    <img src='https://dependencyci.com/github/DongjunLee/kino-bot/badge' alt='Dependency Status' />
  </a>
  
  <a href="https://www.codacy.com/app/humanbrain.djlee/kino-bot?utm_source=github.com&utm_medium=referral&utm_content=DongjunLee/kino-bot&utm_campaign=badger">
    <img src="https://api.codacy.com/project/badge/Grade/401e8a56ebe241daa8b2d0453e16a80c" alt="Codacy">
  </a>
  
</p>



## kino-bot

**Kino** is a **personal assistant** based on **Slack Bot**. It was developed as a personal project to **improve my life quality** by automatically **quantified self**. Various Tracking Tools (cf. RescueTime, Toggl, Todoist) and various third-party (cf. Github, DarkSky, Gbus and etc..) are customized as kino's skill. In addition, kino can automate the parts of everyday life and work. I will also use machine learning and deep learning to grow beyond simple bot to become a smart assistant.  

Kino is getting smarter! **Pull requests** are always welcome. :D


## Feature

- Support **mutiple languages** (Korean and English)
- **Skill** : make your own skill and simply register skill writing function's doc.
- **Scheduler** : jobs(skill) running in background
- Automatic **Tracking**
	- Sleep Time (`Fitbit`)
	- Working Hour (`Toggl`)
	- Tasks (`Todoist` and `Toggl`)
	- Happy & Attention Score
- Notify latest **[Feed](https://github.com/DongjunLee/awesome-feeds)** & Popular Tweet
	- Automatically save to [Pocket](https://getpocket.com/) based on your activity (Feed Catogory Classifier)
- Integrate with **[Giphy](https://giphy.com/)**
- **Customize Webhook** for [IFTTT](https://ifttt.com/) or [Zapier](https://zapier.com)
- Interactive **Dashboard**

### Blog

| Article - Title| English | Korean |
| ------- | ------- | ------- |
| Personal Assistant Kino Part 1 — Overview. | [Medium](https://medium.com/@humanbrain.djlee/personal-assistant-kino-part-1-overview-496b97de4afd) | [Github page](https://dongjunlee.github.io/Personal_Assistant_Kino_Part_1_Overview/) |
| Personal Assistant Kino Part 2 - Skill & Scheduler. | [Medium](https://medium.com/@humanbrain.djlee/personal-assistant-kino-part-2-skill-scheduler-3cf25070fe8e) | [Github page](https://dongjunlee.github.io/Personal_Assistant_Kino_Part_2_Skill_and_Scheduler/) |
| Personal Assistant Kino Part 3 - T3. | [Medium](https://medium.com/@humanbrain.djlee/personal-assistant-kino-part-3-t3-d078b65462be) | [Github page](https://dongjunlee.github.io/Personal_Assistant_Kino_Part_3_T3/) |
| Personal Assistant Kino Part 4 - Smart Feed. | [Medium](https://hackernoon.com/personal-assistant-kino-part-4-smart-feed-b9e4cab966) | [Github page](https://dongjunlee.github.io/Personal_Assistant_Kino_Part_4_Smart_Feed/) |


## Prerequisites

- **[Slack](https://slack.com/)**
- **Python 3.6**


## Quick Start

First, install requirements

```pip install -r requirements.txt```

Second, fill the config.yml (Minimal config)

```yml
bot:
  MASTER_NAME: <name>
  BOT_NAME: Kino
  LANG_CODE: en
  TRIGGER:
    - hey kino
    - 키노야
  ONLY_DIRECT: false   // text startswith Trigger or @kino, or Direct Message
  GIPHY_THRESHOLD: 85  // all responses are random pick number (1~100) to use giphy

slack:
  TOKEN: <token>
  channel:
    DEFAULT: "#general"

```

Finally, just run ```python main.py```.


## Current Skills

kino-bot has **27** skills.

 - :factory: **air_quality** : Air quality forecast. (can use only Korea [airkoreaPy](https://github.com/DongjunLee/airkoreaPy))
 - :writing_hand: **attention_question** : Attention survey after do task.
 - :writing_hand: **attention_report** : Attention Report.
 - :oncoming_bus: **bus_stop** : Bus arrival information. (can use only Korea (gbus api))
 - :sun_with_face: **forecast** : Weather forecast. (using [darksky](https://darksky.net/))
 - :octocat: **github_commit** : Check [Github](https://github.com) push count.
 - :smile: **happy_question** : Happiness survey.
 - :smile: **happy_report** : Happiness Report.
 - :honey_pot: **honeyjam** : **Easter Egg** - Korea Azae Humor (using [honeyjam](https://github.com/DongjunLee/honeyjam)).
 - :building_construction: **jenkins_build** : Build a registered project for Jenkins.
 - :clipboard: **kanban_sync** : Todoist's tasks and Kanban board's card Syncing.
 - :thinking_face: **keep_idea** : Keep idea in Trello board's inbox list.
 - :scales: **maxim_nietzsche** : Nietzsche's Maxim.
 - :thinking_face: **remind_idea** : Remind Trello's inbox card randomly pick.
 - :chart_with_upwards_trend: **rescuetime_efficiency** : RescueTime Efficiency Chart
 - :musical_score: **samhangsi** : I am thinking about the Samhangsi with the kor ballad! (using [char-rnn-tensorflow](https://github.com/DongjunLee/char-rnn-tensorflow))
 - :speech_balloon: **send_message** : Send a text message.
 - :city_sunset: **today_briefing** : Today Briefing - brief Todoist tasks
 - :night_with_stars: **today_summary** : Today summary - **todoist_feedback**, **toggl_report**, **rescuetime_efficiency**, **happy_report**, **attention_report**, **github_commit**
 - :memo: **todoist_feedback** : Feedback from Todoist activity.
 - :page_with_curl: **todoist_remain** : Show todoist's remaining tasks.
 - :bell: **toggl_checker** : Toggl time checker Every 30 minutes.
 - :bar_chart: **toggl_report** : Toggl task Report.
 - :watch: **toggl_timer** : Toggl Timer.
 - :chart: **total_chart** : Overall chart - weekly productivity, happiness, overall score chart.
 - :chart: **total_score** : Overall score  - Productivity (RescueTime, Github Commit, Todoist, Toggl), Mean happiness, mean attention, Exercise, Diary.
 - :crystal_ball: **translate** : Language translation using [Naver Papago api](https://developers.naver.com/docs/nmt/reference/).

## Integration with ML/DL

- [CLaF](https://github.com/naver/claf) : Clova Language Framework
  - [OpenQA](https://github.com/naver/claf#open-qa-drqa): DrQA is a system for reading comprehension applied to open-domain question answering. The system has to combine the challenges of document retrieval (finding the relevant documents) with that of machine comprehension of text (identifying the answers from those documents). 


## License

See the [LICENSE](LICENSE.md) file for license rights and limitations (MIT).