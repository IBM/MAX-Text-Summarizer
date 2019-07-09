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
from core.model import ModelWrapper
from maxfw.core import MAX_API, PredictAPI
from flask_restplus import fields

input_parser = MAX_API.model('ModelInput', {
    'text': fields.List(fields.String, required=True, description=(
        'A list of input text to be summarized. '
        'Each entry in the list is treated as a separate input text and so a summary result will be returned for each entry.'))
})

predict_response = MAX_API.model('ModelPredictResponse', {
    'status': fields.String(required=True, description='Response status message.'),
    'summary_text': fields.List(fields.String, required=True, description=(
        'Generated summary text. Each entry in the list is the summary result for the corresponding entry in the input list.'))
})

logger = logging.getLogger()


class ModelPredictAPI(PredictAPI):

    model_wrapper = ModelWrapper()

    @MAX_API.doc('predict')
    @MAX_API.expect(input_parser, validate=True)
    @MAX_API.marshal_with(predict_response)
    def post(self):
        """Make a prediction given input data"""
        result = {'status': 'error'}
        result['summary_text'] = []

        input_json = MAX_API.payload
        texts = input_json['text']
        for text in texts:
            preds = self.model_wrapper.predict(text)
            result['summary_text'].append(preds)

        result['status'] = 'ok'

        return result
