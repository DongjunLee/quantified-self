# -- coding: utf-8 -*-

import argparse

from hbconfig import Config
import numpy as np
import tensorflow as tf

from .data_loader import TextLoader
from .model import CharRNN


class SamhangSiGenerator:

    SENTENCE_LENGTH = 20

    def __init__(self):
        self._set_data()
        self._make_estimator()

    def _set_data(self):
        data_loader = TextLoader(Config.data.data_dir)
        Config.data.vocab_size = data_loader.vocab_size

        def get_rev_vocab(vocab):
            if vocab is None:
                return None
            return {idx: key for key, idx in vocab.items()}

        self.vocab = data_loader.vocab
        self.rev_vocab = get_rev_vocab(data_loader.vocab)

    def _make_estimator(self):
        params = tf.contrib.training.HParams(**Config.model.to_dict())
        run_config = tf.contrib.learn.RunConfig(model_dir=Config.train.model_dir)

        char_rnn = CharRNN()
        self.estimator = tf.estimator.Estimator(
            model_fn=char_rnn.model_fn,
            model_dir=Config.train.model_dir,
            params=params,
            config=run_config,
        )

    def generate(self, word):
        result = ""
        for char in word:
            result += self._generate_sentence(char)
        return self._combine_sentence(result, word)

    def _generate_sentence(self, char):

        if char not in self.vocab:
            raise ValueError(f"'{char}' is not trained. (can use char in vocab)")

        sample = self.vocab[char]
        sentence = [sample]

        for _ in range(self.SENTENCE_LENGTH):
            X = np.zeros((1, 1), dtype=np.int32)
            X[0, 0] = sample

            predict_input_fn = tf.estimator.inputs.numpy_input_fn(
                x={"input_data": X}, num_epochs=1, shuffle=False
            )

            result = self.estimator.predict(input_fn=predict_input_fn)
            probs = next(result)["probs"]

            def weighted_pick(weights):
                t = np.cumsum(weights)
                s = np.sum(weights)
                return int(np.searchsorted(t, np.random.rand(1) * s))

            sample = weighted_pick(probs)
            sentence.append(sample)

        sentence = list(map(lambda sample: self.rev_vocab.get(sample, ""), sentence))
        sentence = "".join(sentence)
        return sentence

    def _combine_sentence(self, result, word):
        print("word: " + word)
        result = result.replace("\n", " ")
        for char in word[1:]:
            result = result.replace(char, "\n" + char, 1)
        return result


def main(word):
    samhangsi_generator = SamhangSiGenerator()
    result = samhangsi_generator.generate(word)
    print(result)


if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument("--config", type=str, default="config", help="config file name")
    parser.add_argument(
        "--word", type=str, default="삼행시", help="Input Korean word (ex. 삼행시)"
    )
    args = parser.parse_args()

    Config(args.config)
    Config.model.batch_size = 1
    Config.model.seq_length = 1
    print("Config: ", Config)

    main(args.word)
