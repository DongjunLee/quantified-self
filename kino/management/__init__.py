import inspect
import json

from ..functions import Functions
from ..utils.data_handler import DataHandler
from ..utils.logger import Logger



logger = Logger().get_logger()

def write_skills():
    skills = inspect.getmembers(Functions, predicate=inspect.isfunction)
    del skills[0]  # del __init__

    logger.info("start register skills")

    skill_dict = {}
    try:
        for k, v in skills:
            parsed_doc = parse_doc(v.__doc__)
            if parsed_doc is None:
                logger.info(f"{k} skill do not have doc. skip thie skill.")
                continue

            parsed_doc["params"] = list(v.__annotations__.keys())
            skill_dict[k] = parsed_doc
    except BaseException as e:
        logger.exception(v.__doc__)

    data_handler = DataHandler()
    data_handler.write_file("skills.json", skill_dict)

    logger.info(f"kino-bot register {len(skill_dict)} skills.")
    for k, v in skill_dict.items():
        logger.info(f" - {k} : {v.get('description', '')}")

def parse_doc(doc_string):
    if doc_string is None:
        return None

    parsed_doc = {}
    for line in doc_string.splitlines():
        if ":" in line:
            line = line.strip()
            delimeter_index = line.index(":")

            key = line[:delimeter_index]
            value = json.loads(line[delimeter_index+1:])

            parsed_doc[key] = value
    return parsed_doc
