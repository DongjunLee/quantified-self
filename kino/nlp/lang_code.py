import re

from hbconfig import Config
import langid


class LangCode:

    @staticmethod
    def classify(text):
        default_lang_code = Config.bot.get("LANG_CODE", "ko")
        if text is None or text == "":
            return default_lang_code

        cleaned_text = re.sub(r"[0-9]", "", text)  # remove number
        if cleaned_text == "":
            lang_code = default_lang_code
        else:
            lang_code = langid.classify(cleaned_text)[0]
        return lang_code
