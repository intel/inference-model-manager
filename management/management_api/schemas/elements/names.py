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

NAME_REGEX = "^[a-z0-9]([-a-z0-9]*[a-z0-9])?$"

tenant_name = {
    "type": "string",
    "title": "Tenant name",
    "pattern": NAME_REGEX,
    "minLength": 3,
    "maxLength": 63
}

endpoint_name = {
    "type": "string",
    "title": "Endpoint name",
    "pattern": NAME_REGEX,
    "minLength": 3
}

scope_name = {
    "type": "string",
    "title": "Keystone scope name"
}

subject_name = {
    "type": "string",
    "title": "Subject name",
    "pattern": "^(([a-zA-Z0-9]|[a-zA-Z0-9][a-zA-Z0-9\\-]*[a-zA-Z0-9])\\.)*([A-Za-z0-9]|[A-Za-z0-9][A-Za-z0-9\\-]*[A-Za-z0-9])$"  # noqa
}

template_name = {
    "type": "string",
    "title": "Template name",
    "minLength": 3
}
