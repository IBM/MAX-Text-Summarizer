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

import os
import pathlib

# Flask settings
DEBUG = False

# Flask-restplus settings
RESTPLUS_MASK_SWAGGER = False
SWAGGER_UI_DOC_EXPANSION = 'none'

# API metadata
API_TITLE = 'MAX Text Summarizer'
API_DESC = 'Generate a summarized description of an input JSON file.'
API_VERSION = '1.0.0'

# default model
MODEL_NAME = 'get_to_the_point'
ASSET_DIR = pathlib.Path('./assets').absolute()
DEFAULT_MODEL_PATH = os.path.join(ASSET_DIR, MODEL_NAME)
DEFAULT_VOCAB_PATH = os.path.join(ASSET_DIR, 'vocab')
