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

from management_api.schemas.elements.models import model_name, model_version


model_delete_schema = {
    "type": "object",
    "title": "Model DELETE Schema",
    "required": [
        "modelName",
        "modelVersion",
    ],
    "properties": {
        "modelName": model_name,
        "modelVersion": model_version,
    }
}
