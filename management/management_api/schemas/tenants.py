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

from management_api.schemas.elements.names import tenant_name, scope_name
from management_api.schemas.elements.resources import quota
from management_api.schemas.elements.verifications import cert


tenant_post_schema = {
    "type": "object",
    "title": "Tenant POST Schema",
    "required": [
        "name",
        "cert",
        "scope",
        "quota"
    ],
    "properties": {
        "name": tenant_name,
        "cert": cert,
        "scope": scope_name,
        "quota": quota
    }
}

tenant_delete_schema = {
    "type": "object",
    "title": "Tenant DELETE Schema",
    "required": [
        "name"
    ],
    "properties": {
        "name": tenant_name
    }
}
