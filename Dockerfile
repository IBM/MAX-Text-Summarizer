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

FROM codait/max-base:v1.1.3

# Fill in these with a link to the bucket containing the model and the model file name
ARG model_bucket=https://max.cdn.appdomain.cloud/max-text-summarizer/1.0.0
ARG model_file=assets.tar.gz

WORKDIR /workspace

RUN wget -nv --show-progress --progress=bar:force:noscroll ${model_bucket}/${model_file} --output-document=assets/${model_file} && \
  tar -x -C assets/ -f assets/${model_file} -v && rm assets/${model_file}

COPY requirements.txt /workspace
RUN pip install -r requirements.txt

COPY . /workspace

# check file integrity
RUN md5sum -c md5sums.txt && \
  echo Ensuring that all model files are md5sum-checked... && \
  echo Checked files: && export MD5_FILES="$(awk '{print $2}' md5sums.txt | xargs realpath | sort)" && echo "$MD5_FILES" && \
  echo Model files: && export MODEL_FILES="$(find assets -type f | xargs realpath | sort)" && echo "$MODEL_FILES" && \
  test "$MD5_FILES" = "$MODEL_FILES"

EXPOSE 5000

CMD python app.py
