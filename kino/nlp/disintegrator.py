import re
import string

from konlpy.tag import Twitter

import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.corpus import wordnet
from nltk.stem.wordnet import WordNetLemmatizer

from .lang_code import LangCode


class Disintegrator:
    def __init__(self, text):
        self.text = text
        lang_code = LangCode.classify(text)
        if lang_code == "ko":
            self.instance = KorDisintegrator()
        elif lang_code == "en":
            self.instance = EngDisintegrator()
        else:
            self.instance = None

    def convert2simple(self):
        if self.instance is None:
            return ""

        try:
            return self.instance.convert2simple(sentence=self.text)
        except BaseException:
            return ""


class KorDisintegrator:
    def __init__(self):
        self.ko_twitter = Twitter()

    def convert2simple(self, sentence="", norm=True, stem=True):
        disintegrated_sentence = self.ko_twitter.pos(sentence, norm=norm, stem=stem)
        convert_sentence = []

        for w, t in disintegrated_sentence:
            if t not in ["Eomi", "Josa", "KoreanParticle", "Punctuation"]:
                convert_sentence.append(w)
        return " ".join(convert_sentence)


class EngDisintegrator:
    def __init__(self):
        self.stopwords = set(stopwords.words("english"))
        self.lemmatizer = WordNetLemmatizer()

    def convert2simple(self, sentence=""):
        tokenized = word_tokenize(sentence)
        tokenized = self.__filter_punctuation(tokenized)
        tokenized = self.__filter_stopwords(tokenized)
        return " ".join(self.__lemmatize(tokenized))

    def __filter_punctuation(self, tokenized):
        regex = re.compile("[%s]" % re.escape(string.punctuation))

        tokenized_no_punctuation = []

        for token in tokenized:
            new_token = regex.sub("", token)
            if not new_token == "":
                tokenized_no_punctuation.append(new_token)
        return tokenized_no_punctuation

    def __filter_stopwords(self, tokenized):
        return [t for t in tokenized if t not in self.stopwords]

    def __lemmatize(self, tokenized):
        lemmatized_tokens = []
        for tag in nltk.pos_tag(tokenized):
            lemmatized_tokens.append(
                self.lemmatizer.lemmatize(tag[0], self.__get_wordnet_pos(tag[1]))
            )
        return lemmatized_tokens

    def __get_wordnet_pos(self, treebank_tag):

        if treebank_tag.startswith("J"):
            return wordnet.ADJ
        elif treebank_tag.startswith("V"):
            return wordnet.VERB
        elif treebank_tag.startswith("N"):
            return wordnet.NOUN
        elif treebank_tag.startswith("R"):
            return wordnet.ADV
        else:
            return ""
