import codecs
import os
import collections
from six.moves import cPickle
import numpy as np


class TextLoader():

    def __init__(self, data_dir, batch_size=None, seq_length=None, encoding='utf-8'):
        self.data_dir = data_dir
        self.batch_size = batch_size
        self.seq_length = seq_length
        self.encoding = encoding

        input_file = os.path.join(data_dir, "input.txt")
        vocab_file = os.path.join(data_dir, "vocab.pkl")
        tensor_file = os.path.join(data_dir, "data.npy")

        if not (os.path.exists(vocab_file) and os.path.exists(tensor_file)):
            print("reading text file")
            self.preprocess(input_file, vocab_file, tensor_file)
        else:
            print("loading preprocessed files")
            self.load_preprocessed(vocab_file, tensor_file)

    def preprocess(self, input_file, vocab_file, tensor_file):
        with codecs.open(input_file, "r", encoding=self.encoding) as f:
            data = f.read()
        counter = collections.Counter(data)
        count_pairs = sorted(counter.items(), key=lambda x: -x[1])
        self.chars, _ = zip(*count_pairs)
        self.vocab_size = len(self.chars)
        self.vocab = dict(zip(self.chars, range(len(self.chars))))
        with open(vocab_file, 'wb') as f:
            cPickle.dump(self.chars, f)
        self.tensor = np.array(list(map(self.vocab.get, data)))
        np.save(tensor_file, self.tensor)

    def load_preprocessed(self, vocab_file, tensor_file):
        with open(vocab_file, 'rb') as f:
            self.chars = cPickle.load(f)
        self.vocab_size = len(self.chars)
        self.vocab = dict(zip(self.chars, range(len(self.chars))))
        self.tensor = np.load(tensor_file)

    def make_train_and_test_set(self, train_size=0.8, test_size=0.2):
        self.num_batches = int(self.tensor.size / (self.batch_size *
                                                   self.seq_length))

        # When the data (tensor) is too small,
        # let's give them a better error message
        if self.num_batches == 0:
            assert False, "Not enough data. Make seq_length and batch_size small."
        if train_size + test_size > 1 :
            assert False, "train_size and test_size are large. sum > 1"

        self.tensor = self.tensor[:self.num_batches * self.batch_size * self.seq_length]
        xdata = self.tensor
        ydata = np.copy(self.tensor)
        ydata[:-1] = xdata[1:]
        ydata[-1] = xdata[0]

        self.X = xdata
        self.y = ydata

        train_length = int(len(self.X) / self.seq_length * train_size) * self.seq_length
        test_length = int(len(self.X) / self.seq_length * test_size) * self.seq_length

        train_X = self.X[train_length:]
        train_y = self.y[train_length:]

        test_X = self.X[:test_length]
        test_y = self.y[:test_length]

        return train_X, test_X, train_y, test_y

    def create_batches(self):
        self.num_batches = int(self.tensor.size / (self.batch_size *
                                                   self.seq_length))

        self.X_batches = np.split(self.X.reshape(self.batch_size, -1),
                                  self.num_batches, 1)
        self.y_batches = np.split(self.y.reshape(self.batch_size, -1),
                                  self.num_batches, 1)
        self.reset_batch_pointer()

    def next_batch(self):
        X, y = self.x_batches[self.pointer], self.y_batches[self.pointer]
        self.pointer += 1
        return X, y

    def reset_batch_pointer(self):
        self.pointer = 0
