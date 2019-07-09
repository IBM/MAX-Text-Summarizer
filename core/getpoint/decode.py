# Copyright 2016 The TensorFlow Authors. All Rights Reserved.
# Modifications Copyright 2017 Abigail See
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================

"""This file contains code to run beam search decoding, including running ROUGE evaluation and producing JSON datafiles for the in-browser attention visualizer, which can be found here https://github.com/abisee/attn_vis"""

import os
import sys
import time
import tensorflow as tf
import beam_search
import data
import json
import pyrouge
import util
import logging
import numpy as np

FLAGS = tf.app.flags.FLAGS

SECS_UNTIL_NEW_CKPT = 60  # max number of seconds before loading new checkpoint


class BeamSearchDecoder(object):
  """Beam search decoder."""

  def __init__(self, model, batcher, vocab):
    """Initialize decoder.

    Args:
      model: a Seq2SeqAttentionModel object.
      batcher: a Batcher object.
      vocab: Vocabulary object
    """
    self._model = model
    self._model.build_graph()
    self._batcher = batcher
    self._vocab = vocab
    self._saver = tf.train.Saver() # we use this to load checkpoints for decoding
    self._sess = tf.Session(config=util.get_config())

    # Load an initial checkpoint to use for decoding
    ckpt_path = util.load_ckpt(self._saver, self._sess)


    # if FLAGS.single_pass:
    #   # Make a descriptive decode directory name
    #   ckpt_name = "ckpt-" + ckpt_path.split('-')[-1] # this is something of the form "ckpt-123456"
    #   self._decode_dir = os.path.join(FLAGS.log_root, get_decode_dir_name(ckpt_name))
    #   if os.path.exists(self._decode_dir):
    #     raise Exception("single_pass decode directory %s should not already exist" % self._decode_dir)
    #
    # else: # Generic decode dir name
    self._decode_dir = os.path.join(FLAGS.log_root, "decode")

    # Make the decode dir if necessary
    if not os.path.exists(self._decode_dir): os.mkdir(self._decode_dir)

    # if FLAGS.single_pass:
    #   # Make the dirs to contain output written in the correct format for pyrouge
    #   self._rouge_ref_dir = os.path.join(self._decode_dir, "reference")
    #   if not os.path.exists(self._rouge_ref_dir): os.mkdir(self._rouge_ref_dir)
    #   self._rouge_dec_dir = os.path.join(self._decode_dir, "decoded")
    #   if not os.path.exists(self._rouge_dec_dir): os.mkdir(self._rouge_dec_dir)


  def decode(self):
    """Decode examples until data is exhausted (if FLAGS.single_pass) and return, or decode indefinitely, loading latest checkpoint at regular intervals"""
    # t0 = time.time()
    batch = self._batcher.next_batch()  # 1 example repeated across batch

    original_article = batch.original_articles[0]  # string
    original_abstract = batch.original_abstracts[0]  # string

    # input data
    article_withunks = data.show_art_oovs(original_article, self._vocab) # string
    abstract_withunks = data.show_abs_oovs(original_abstract, self._vocab, (batch.art_oovs[0] if FLAGS.pointer_gen else None)) # string

    # Run beam search to get best Hypothesis
    best_hyp = beam_search.run_beam_search(self._sess, self._model, self._vocab, batch)

    # Extract the output ids from the hypothesis and convert back to words
    output_ids = [int(t) for t in best_hyp.tokens[1:]]
    decoded_words = data.outputids2words(output_ids, self._vocab, (batch.art_oovs[0] if FLAGS.pointer_gen else None))

    # Remove the [STOP] token from decoded_words, if necessary
    try:
      fst_stop_idx = decoded_words.index(data.STOP_DECODING) # index of the (first) [STOP] symbol
      decoded_words = decoded_words[:fst_stop_idx]
    except ValueError:
      decoded_words = decoded_words
    decoded_output = ' '.join(decoded_words) # single string

    # tf.logging.info('ARTICLE:  %s', article)
    #  tf.logging.info('GENERATED SUMMARY: %s', decoded_output)

    sys.stdout.write(decoded_output)
