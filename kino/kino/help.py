import slack

class Guide(object):

    def __init__(self):
        self.slackbot = slack.SlackerAdapter()
        self.template = slack.MsgTemplate()

    def help(self):
        attachments = self.template.make_help_template(self.__guide(), self.__example())
        self.slackbot.send_message(attachments=attachments)

    def __guide(self):
        guide_msg = "Kino는 Slack Bot으로 기본으로 개발된 Personal Assistant A.I 입니다.\n"
        guide_msg += "필요한 기능이 있으면 그때그때 개발하면서 똑똑해지고 있습니다.\n"
        guide_msg += "현재는 시간에 따라 실행하고자 하는 함수를 등록할 수 있고, 입력에 따른 답을 하는 수준입니다..\n\n"
        guide_msg += "아래 사용할 수 있는 기능 예시들 입니다. "
        return guide_msg

    def __example(self):
        example = {
            "Greeting": "키노야 안녕",
            "Worker": "키노야 일 시작하자, 일이 있어! 2 시간마다 날씨예보, 일 추가 20시에 하루 요약",
            "Notifier": "알람 등록해줘, 알람 보여줘, 알람 삭제",
            "Between": "시간대 추가해줘, 시간대 보자, 시간대 제거해줘",
            "Functions": "기능 뭐 있어?",
            "Weather": "지금 날씨 예보, 오늘 날씨 어때?, 주간 날씨 알려줘.",
            "Todoist": "하루 브리핑 하자!, 오늘 하루 요약해줘.",
            "Github": "일일 커밋 했나?, 주간 커밋 보여줘",
            "Toggl": "toggl, 작업시간 알려줘, 시간체크, 토글 리포트 만들어줘, 상세 작업 리포트 보여줘",
            "Maxim": "니체 명언"
        }
        return example
