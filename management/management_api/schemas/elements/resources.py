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

from copy import deepcopy


RESOURCE_REGEX = "^([+]?[0-9.]+)([eEinumkKMGTP]*[+]?[0-9]*)$"

resources_dict = {
    "type": "string",
    "optional": True,
    "pattern": RESOURCE_REGEX
}

resources = {
    "type": "object",
    "title": "Resource quota",
    "properties": {
        "requests.cpu": resources_dict,
        "limits.cpu": resources_dict,
        "requests.memory": resources_dict,
        "limits.memory": resources_dict
    }
}

max_endpoints = {
    "type": "integer",
    "optional": True,
    "title": "maxEndpoints",
    "minimum": 1
}

quota = deepcopy(resources)
quota["properties"]["maxEndpoints"] = max_endpoints

replicas = {
    "type": "integer",
    "optional": True,
    "title": "Replicas",
    "minimum": 0
}
