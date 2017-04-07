
from konlpy.tag import Twitter


class Disintegrator(object):

    def __init__(self):
        self.ko_twitter = Twitter()

    def convert2simple(self, sentence="", norm=True, stem=True):
        disintegrated_sentence = self.ko_twitter.pos(
            sentence, norm=norm, stem=stem)
        convert_sentence = []

        for w, t in disintegrated_sentence:
            if t not in ['Eomi', 'Josa', 'KoreanParticle', 'Punctuation']:
                convert_sentence.append(w)
        return " ".join(convert_sentence)
