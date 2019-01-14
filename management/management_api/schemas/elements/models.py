#
# Copyright (c) 2018 Intel Corporation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

VERSION_POLICY_REGEX = "^\s*{\s*(specific\s*{\s*(versions:\s*\d+\s+)*versions:\s*\d+\s*}|all\s*{\s*}|latest\s*{\s*})\s*}\s*$"  # noqa

model_name = {
    "type": "string",
    "title": "Model name",
    "minLength": 3
}

model_version = {
    "type": "integer",
    "title": "Model version",
    "minimum": 1
}

model_version_policy = {
    "type": "string",
    "title": "Model version policy",
    "pattern": VERSION_POLICY_REGEX,
}

file_name = {
    "type": "string",
    "title": "Model file name"
}

upload_id = {
    "type": "string",
    "title": "Upload ID to identify whose part is being uploaded"
}

parts = {
    "type": "array",
    "title": "Parts of uploads"
}
