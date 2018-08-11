import inspect
import json

from ..functions import Functions
from ..utils.data_handler import DataHandler
from ..utils.data_loader import SkillData
from ..utils.data_loader import FeedData


def register_skills():
    skills = inspect.getmembers(Functions, predicate=inspect.isfunction)
    del skills[0]  # del __init__

    print("start register skills")

    skill_dict = {}
    try:
        for k, v in skills:
            parsed_doc = parse_doc(v.__doc__)
            if parsed_doc is None:
                print(f"{k} skill do not have doc. skip thie skill.")
                continue

            parsed_doc["params"] = list(v.__annotations__.keys())
            skill_dict[k] = parsed_doc
    except BaseException as e:
        print(v.__doc__)

    data_handler = DataHandler()
    data_handler.write_file("skills.json", skill_dict)

    print(f"kino-bot has **{len(skill_dict)}** skills.")
    for k, v in skill_dict.items():
        print(
            f" - {v.get('icon', ':white_small_square: ')}**{k}** : {v.get('description', '')}"
        )


def parse_doc(doc_string):
    if doc_string is None:
        return None

    parsed_doc = {}
    for line in doc_string.splitlines():
        if ":" in line:
            line = line.strip()
            delimeter_index = line.index(":")

            key = line[:delimeter_index]
            value = json.loads(line[delimeter_index + 1 :])

            parsed_doc[key] = value
    return parsed_doc


def prepare_skill_data():
    print("setting skill logs for Skill Predictor ...")
    SkillData()


def prepare_feed_data():
    print("setting feed and pocket logs for Feed Classifier ...")
    FeedData()
