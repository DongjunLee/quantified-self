
class MessageResource:
    ERROR = "에러가 발생하였습니다."
    NOT_UNDERSTANDING = "무슨 말인지 잘 모르겠어요. 저를 똑똑하게 만들어주세요!!"
    CREATE = "등록이 완료되었습니다!"
    EMPTY = "비어있습니다. 새로 등록해주세요!."
    READ = "등록된 리스트입니다."
    UPDATE = "변경이 완료되었습니다."
    DELETE = "삭제 완료!"
    NOTIFIER_START = "Notifier 기능을 시작합니다."
    NOTIFIER_STOP = "Notifier 기능을 중지합니다."

    GUIDE = "Kino에 대한 간략한 소개 및 도움말 입니다."

    SCHEDULER_CREATE_START = "알람 등록을 진행합니다."
    SCHEDULER_CREATE_STEP1 = "반복 알람을 사용할 경우는 시간대를 선택 하시고,\n 한 번 알리는 경우 새로운 시간을 입력해주세요!\n (ex. #1 or 10:00)"
    SCHEDULER_CREATE_STEP1_ONLY_TIME = "시간을 입력해주세요!\n (ex. 10:00)"
    SCHEDULER_CREATE_STEP2 = "다음으로 주기를 입력해주세요!\n (ex. 30 분)"
    SCHEDULER_CREATE_STEP3 = "사용될 함수는 무엇인가요?\n (ex. send_message, {\"text\"=\"Test!\"})"

    SCHEDULER_DELETE_START = "알람 삭제를 진행합니다.\n지우고자 하시는 알람의 인덱스를 입력해주세요!"

    BETWEEN_CREATE_START = "시간대 등록을 진행합니다."
    BETWEEN_CREATE_STEP1 = "시간간격을 입력해주세요!\n(ex. 12:00~19:00)"
    BETWEEN_CREATE_STEP2 = "입력하신 시간대를 설명해주시겠어요?\n (ex. 업무 시간)"

    BETWEEN_DELETE_START = "시간대 삭제를 진행합니다.\n지우고자 하시는 시간대의 인덱스를 입력해주세요!"

    GITHUB_COMMIT_EMPTY = "Github에 Commit한 기록이 없습니다. 일일커밋 실천하셔야죠!"
    GITHUB_COMMIT_EXIST = "오, Commit을 하셨군요! 멋지십니다.ㅎㅎ 오늘 하루 Commit 수 : "

    ROBOT_ICON = ":robot_face: "
    TIMER_ICON = ":mantelpiece_clock: "
    WHITE_LIST_ICON = ":white_medium_small_square: "
    WHITE_ELEMENT_ICON = "   :white_circle: "
    BLACK_LIST_ICON = ":black_medium_small_square: "
    BLACK_ELEMENT_ICON = "   :black_circle: "
    BLUE_DIAMOND_ICON = ":small_blue_diamond: "
    ORANGE_DIAMOND_ICON = ":small_orange_diamond: "
    SEND_MESSAGE_ICON = ":speech_balloon: "
    DAILY_COMMIT_ICON = ":octocat: "

    WEATHER = "날씨 정보를 알려드립니다."
    WEATHER_ICON = ":full_moon_with_face: "
    WEATHER_ICONS = {
        "clear-day": ":sunny: ",
        "clear-night": ":first_quarter_moon_with_face: ",
        "rain": ":umbrella_with_rain_drops: ",
        "snow": ":snowman: ",
        "sleet": ":snow_cloud: ",
        "wind": ":wind_blowing_face: ",
        "fog": ":fog: ",
        "cloudy": ":cloud: ",
        "partly-cloudy-day": ":partly_sunny: ",
        "partly-cloudy-night": ":night_with_stars: "
    }
