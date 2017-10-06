import random
import requests



class Humor:

    HONEYJAM_URL = "https://raw.githubusercontent.com/DongjunLee/honeyjam/master/README.md"

    def __init__(self):
        pass

    def honeyjam(self):
        r = requests.get(self.HONEYJAM_URL)
        questions, answers = self._make_questions_and_answers(r.text)

        humor_count = len(questions)
        ran_index = random.randint(1, humor_count)

        return questions[ran_index], answers[ran_index]

    def _make_questions_and_answers(self, content):
        remove_front = content[content.index("---")+3:]
        remove_front_and_footer = remove_front[:remove_front.index("###")]
        content = remove_front_and_footer

        questions = []
        answers = []

        for line in content.splitlines():
            if line == "":
                continue

            if line.startswith("*"):
                questions.append(line.replace("* ", ""))
            elif line.startswith("\t"):
                answers.append(line.replace("\t* ", ""))
            else:
                raise ValueError("honeyjam format error")

        return questions, answers
