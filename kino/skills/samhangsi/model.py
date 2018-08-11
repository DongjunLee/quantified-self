from hbconfig import Config
import numpy as np
import tensorflow as tf


class CharRNN:
    def __init__(self):
        pass

    def model_fn(self, mode, features, labels, params):
        self.mode = mode
        self.params = params

        self.input_data = features
        self.targets = labels

        if type(features) == dict:
            self.input_data = features["input_data"]

        self.build_graph()

        if mode == tf.estimator.ModeKeys.PREDICT:
            return tf.estimator.EstimatorSpec(
                mode=mode, predictions={"probs": self.probs}
            )

        return tf.estimator.EstimatorSpec(
            mode=mode, predictions=None, loss=self.loss, train_op=self.train_op
        )

    def build_graph(self):
        self._create_embedding()
        self._create_rnn_cell()
        self._create_inferece()
        self._create_predictions()

        if self.mode == tf.estimator.ModeKeys.PREDICT:
            pass
        else:
            self._create_loss()
            self._creat_train_op()

    def _create_embedding(self):
        self.embedding = tf.get_variable(
            "embedding", [Config.data.vocab_size, self.params.rnn_size]
        )

    def _create_rnn_cell(self):
        cells = []
        for _ in range(self.params.num_layers):
            cell = tf.contrib.rnn.GRUCell(self.params.rnn_size)
            if self.mode == tf.estimator.ModeKeys.TRAIN:
                cell = tf.contrib.rnn.DropoutWrapper(
                    cell,
                    input_keep_prob=self.params.input_keep_prob,
                    output_keep_prob=self.params.output_keep_prob,
                )
            cells.append(cell)
        self.rnn_cells = tf.contrib.rnn.MultiRNNCell(cells, state_is_tuple=True)
        self.initial_state = self.rnn_cells.zero_state(
            self.params.batch_size, tf.float32
        )

    def _create_inferece(self):

        with tf.variable_scope("rnnlm"):
            softmax_w = tf.get_variable(
                "softmax_w", [self.params.rnn_size, Config.data.vocab_size]
            )
            softmax_b = tf.get_variable("softmax_b", [Config.data.vocab_size])

        inputs = tf.nn.embedding_lookup(self.embedding, self.input_data)

        if self.mode == tf.estimator.ModeKeys.TRAIN and self.params.output_keep_prob:
            inputs = tf.nn.dropout(inputs, self.params.output_keep_prob)

        inputs = tf.split(inputs, self.params.seq_length, 1)
        inputs = [tf.squeeze(input_, [1]) for input_ in inputs]

        def loop(prev, _):
            prev = tf.matmul(prev, softmax_w) + softmax_b
            prev_symbol = tf.stop_gradient(tf.argmax(prev, 1))
            return tf.nn.embedding_lookup(self.embedding, prev_symbol)

        is_training = self.mode == tf.estimator.ModeKeys.TRAIN
        outputs, last_state = tf.contrib.legacy_seq2seq.rnn_decoder(
            inputs,
            self.initial_state,
            self.rnn_cells,
            loop_function=loop if not is_training else None,
            scope="rnnlm",
        )
        output = tf.reshape(tf.concat(outputs, 1), [-1, self.params.rnn_size])

        self.logits = tf.matmul(output, softmax_w) + softmax_b
        self.probs = tf.nn.softmax(self.logits, name="probs")

    def _create_predictions(self):
        self.predictions = tf.argmax(self.probs, axis=1)
        tf.identity(self.predictions[: self.params.seq_length], "prediction_0")

    def _create_loss(self):
        sequnece_loss = tf.contrib.legacy_seq2seq.sequence_loss_by_example(
            [self.logits],
            [tf.reshape(self.targets, [-1])],
            [tf.ones([self.params.batch_size * self.params.seq_length])],
        )
        self.loss = (
            tf.reduce_sum(sequnece_loss, name="loss/reduce_sum")
            / self.params.batch_size
            / self.params.seq_length
        )

    def _creat_train_op(self):
        self.train_op = tf.contrib.layers.optimize_loss(
            loss=self.loss,
            global_step=tf.contrib.framework.get_global_step(),
            optimizer=tf.train.AdamOptimizer,
            learning_rate=Config.train.learning_rate,
        )
