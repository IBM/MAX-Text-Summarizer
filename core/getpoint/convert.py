import os
import sys
import argparse
import struct
import tensorflow as tf
from tensorflow.core.example import example_pb2


END_TOKENS = frozenset(['.', '!', '?', '...', "'", "`", '"', ")"]) # acceptable ways to end a sentence

def fix_missing_period(line):
  """Adds a period to a line that is missing a period"""
  if "@highlight" in line: return line
  if line=="": return line
  if line[-1] in END_TOKENS: return line
  return line + " ."

def get_art_abs(input_string):
  lines = input_string.splitlines()
  lines = [line.lower() for line in lines]
  lines = [fix_missing_period(line) for line in lines]

  article_lines = []
  highlights = []
  next_is_highlight = False
  for idx,line in enumerate(lines):
    if line == "":
      continue # no line
    elif line.startswith("@highlight"):
      next_is_highlight = True
    elif next_is_highlight:
      highlights.append(line)
    else:
      article_lines.append(line)

  # To a string
  article = ' '.join(article_lines)

  return article

def convert_to_bin(input_string, out_file):

  with open(out_file, 'wb') as writer:
    # start to write .bin file
    article = get_art_abs(input_string)

    article=tf.compat.as_bytes(article, encoding='utf-8')
    # tf.Example write
    tf_example = example_pb2.Example()
    tf_example.features.feature['article'].bytes_list.value.extend([article])
    tf_example_str = tf_example.SerializeToString()
    str_len = len(tf_example_str)
    writer.write(struct.pack('q', str_len))
    writer.write(struct.pack('%ds' % str_len, tf_example_str))
