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

import requests
import json

from management_api_tests.config import DEFAULT_HEADERS, ADMIN_HEADERS, SCOPE_NAME, \
    TENANT_RESOURCES, SENSIBLE_ENDPOINT_RESOURCES, TENANTS_MANAGEMENT_API_URL, \
    ENDPOINTS_MANAGEMENT_API_URL
from e2e_tests.config import TENANT_NAME, MODEL_NAME, CERT


def create_tenant(name=TENANT_NAME, headers=ADMIN_HEADERS,
                  scope=SCOPE_NAME, resources=TENANT_RESOURCES, cert=CERT):
    data = json.dumps({
        'name': name,
        'cert': cert,
        'scope': scope,
        'quota': resources,
    })
    url = TENANTS_MANAGEMENT_API_URL

    response = requests.post(url, data=data, headers=headers, verify=False)
    return response


def delete_tenant(headers=ADMIN_HEADERS, name=TENANT_NAME):
    url = TENANTS_MANAGEMENT_API_URL
    data = json.dumps({
        'name': name,
    })
    response = requests.delete(url, data=data, headers=headers, verify=False)
    return response


def create_endpoint(headers=DEFAULT_HEADERS, name=MODEL_NAME,
                    resources=SENSIBLE_ENDPOINT_RESOURCES,
                    tenant=TENANT_NAME):
    data = json.dumps({
        'modelName': name,
        'modelVersion': 1,
        'endpointName': name + 'endpoint',
        'subjectName': 'client',
        'resources': resources,
        'templateName': 'tf-serving',
    })
    url = ENDPOINTS_MANAGEMENT_API_URL.format(tenant_name=tenant)

    response = requests.post(url, data=data, headers=headers, verify=False)
    return response
