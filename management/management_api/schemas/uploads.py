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

from management_api.schemas.elements.models import model_name, model_version, upload_id, \
    file_name, parts, dir

multipart_start_schema = {
    "type": "object",
    "title": "Multipart upload start schema",
    "required": [
        "modelName",
        "modelVersion",
        "fileName"
    ],
    "properties": {
        "modelName": model_name,
        "modelVersion": model_version,
        "fileName": file_name
    }
}

multipart_done_schema = {
    "type": "object",
    "title": "Multipart upload done schema",
    "required": [
        "modelName",
        "modelVersion",
        "fileName",
        "uploadId",
        "parts"
    ],
    "properties": {
        "modelName": model_name,
        "modelVersion": model_version,
        "fileName": file_name,
        "uploadId": upload_id,
        "parts": parts
    }
}

multipart_abort_schema = {
    "type": "object",
    "title": "Multipart upload abort schema",
    "required": [
        "modelName",
        "modelVersion",
        "fileName",
        "uploadId"
    ],
    "properties": {
        "modelName": model_name,
        "modelVersion": model_version,
        "fileName": file_name,
        "uploadId": upload_id
    }
}

upload_dir_schema = {
    "type": "object",
    "title": "Create directory inside bucket",
    "required": [
        "key"
    ],
    "properties": {
        "key": dir
    }
}
