#
# Copyright 2018-2019 IBM Corp. All Rights Reserved.
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
#

import logging
import os
from pathlib import Path
from subprocess import Popen, PIPE
from tempfile import NamedTemporaryFile, TemporaryDirectory
from threading import Lock
from flask import abort

from maxfw.model import MAXModelWrapper
from config import ASSET_DIR, DEFAULT_MODEL_PATH, DEFAULT_VOCAB_PATH, MODEL_NAME

from .getpoint.convert import convert_to_bin
from .util import process_punctuation

logger = logging.getLogger()


class ModelWrapper(MAXModelWrapper):

    MODEL_META_DATA = {
        'id': 'max-text-summarizer',
        'name': 'MAX Text Summarizer',
        'description': '{} TensorFlow model trained on CNN/Daily Mail Data'.format(MODEL_NAME),
        'type': 'Text Analysis',
        'source': 'https://developer.ibm.com/exchanges/models/all/max-text-summarizer/',
        'license': 'Apache V2'
    }

    _tempfile_mutex = Lock()

    def __init__(self, path=DEFAULT_MODEL_PATH):
        logger.info('Loading model from: %s...', path)

        self.log_dir = TemporaryDirectory()
        self.p_summarize = Popen(['python', 'core/getpoint/run_summarization.py', '--mode=decode',
                                  '--ckpt_dir={}'.format(ASSET_DIR),
                                  '--vocab_path={}'.format(DEFAULT_VOCAB_PATH),
                                  '--log_root={}'.format(self.log_dir.name)],
                                 stdin=PIPE, stdout=PIPE)

    def __del__(self):
        self.p_summarize.stdin.close()
        self.log_dir.cleanup()

    def _pre_process(self, x):
        return process_punctuation(x)

    def _predict(self, x):
        if all(not c.isalpha() for c in x):
            abort(400, 'Input file contains no alphabetical characters.')

        with __class__._tempfile_mutex:
            # Create temporary file for inter-process communication. This
            # procedure must be not executed by two threads at the same time to
            # avoid file name conflicts.
            try:
                # Make use of tmpfs on Linux if available.
                directory = Path("/dev/shm/max-ts-{}".format(os.getpid()))
                # The following two lines may also raise IOError
                directory.mkdir(parents=True, exist_ok=True)
                bin_file = NamedTemporaryFile(
                    prefix='generated_sample_', suffix='.bin',
                    dir=directory.absolute())
            except IOError as e:
                logger.warning('Failed to create temporary file in RAM. '
                               'Fall back to disk files: %s', e)
                directory = Path("./assets/max-ts-{}".format(os.getpid()))
                directory.mkdir(parents=True, exist_ok=True)
                bin_file = NamedTemporaryFile(
                    prefix='generated_sample_', suffix='.bin',
                    dir=directory.absolute())

        with bin_file:

            bin_file_path = bin_file.name

            convert_to_bin(x, bin_file_path)

            try:
                self.p_summarize.stdin.write(bin_file_path.encode('utf8'))
                self.p_summarize.stdin.write(b'\n')
                self.p_summarize.stdin.flush()
                # One paragraph at a time under our usage.
                summary = self.p_summarize.stdout.readline()
            except (IOError, BrokenPipeError) as e:
                err_msg = 'Failed to communicate with the summarizer.'
                logger.error(err_msg + ' %s', e)
                abort(400, err_msg)

        summary = summary.decode('utf-8')

        if len(summary) <= len(x):
            return summary

        # Truncate the summary length to be no longer than x. Note that x already has its punctuations processed.
        if not summary[len(x)].isspace():  # We are truncating the middle of a word. Also remove the last word
            return summary[:len(x)].rsplit(maxsplit=1)[0]
        else:
            return summary[:len(x)]
