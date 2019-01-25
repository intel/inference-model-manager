#
# Copyright (c) 2018-2019 Intel Corporation
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

from management_api_tests.config import SCOPE_NAME

from e2e_tests.config import TENANT_NAME, MODEL_NAME
from config import CERT, ADMIN_HEADERS, TENANT_RESOURCES, TENANTS_MANAGEMENT_API_URL, \
    DEFAULT_HEADERS, ENDPOINTS_MANAGEMENT_API_URL, \
    ENDPOINT_MANAGEMENT_API_URL


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


def create_endpoint(params: dict, headers=DEFAULT_HEADERS, tenant=TENANT_NAME):
    data = json.dumps(params)
    url = ENDPOINTS_MANAGEMENT_API_URL.format(tenant_name=tenant)

    response = requests.post(url, data=data, headers=headers, verify=False)
    return response


def update_endpoint(params: dict, headers=DEFAULT_HEADERS, name=MODEL_NAME,
                    tenant=TENANT_NAME):
    data = json.dumps(params)
    url = ENDPOINT_MANAGEMENT_API_URL.format(tenant_name=tenant, endpoint_name=name + 'endpoint')

    response = requests.patch(url, data=data, headers=headers, verify=False)
    return response
