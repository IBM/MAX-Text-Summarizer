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

import glob
import json
import pytest
import requests


MODEL_PREDICT_ENDPOINT = 'http://localhost:5000/model/predict'


def test_swagger():

    model_endpoint = 'http://localhost:5000/swagger.json'

    r = requests.get(url=model_endpoint)
    assert r.status_code == 200
    assert r.headers['Content-Type'] == 'application/json'

    json = r.json()
    assert 'swagger' in json
    assert json.get('info').get('title') == 'MAX Text Summarizer'
    assert json.get('info').get('description') == 'Generate a summarized description of an input document.'


def test_metadata():

    model_endpoint = 'http://localhost:5000/model/metadata'

    r = requests.get(url=model_endpoint)
    assert r.status_code == 200

    metadata = r.json()
    assert metadata['id'] == 'max-text-summarizer'
    assert metadata['name'] == 'MAX Text Summarizer'
    assert metadata['description'] == 'get_to_the_point TensorFlow model trained on CNN/Daily Mail Data'
    assert metadata['license'] == 'Apache V2'


def test_predict_valid():
    "Test prediction for valid input."
    short_text = 'Why not summarize?'
    with open('samples/sample1.json') as f:
        long_text = json.load(f)['text'][0]

    json_data = {
        'text': [short_text, long_text]
    }

    r = requests.post(url=MODEL_PREDICT_ENDPOINT, json=json_data)

    assert r.status_code == 200
    response = r.json()
    assert response['status'] == 'ok'
    assert len(response['summary_text']) == 2


def test_predict_sample():
    "Test prediction for sample inputs."
    for sample in glob.iglob('samples/*.json'):
        with open(sample) as f:
            json_data = json.load(f)

        r = requests.post(url=MODEL_PREDICT_ENDPOINT, json=json_data)

        assert r.status_code == 200
        response = r.json()
        assert response['status'] == 'ok'
        assert len(response['summary_text']) == len(json_data['text'])


def test_predict_invalid_input_no_string():
    "Test invalid input: no string."
    json_data = {}
    r = requests.post(url=MODEL_PREDICT_ENDPOINT, json=json_data)
    assert r.status_code == 400


def test_predict_invalid_empty_string():
    "Test invalid input: empty and blank strings."
    for s in ('', ' \t\f\r\n'):
        for text in ([s], ['some text', s]):
            json_data = {'text': text}
            r = requests.post(url=MODEL_PREDICT_ENDPOINT, json=json_data)
            assert r.status_code == 400


if __name__ == '__main__':
    pytest.main([__file__])
