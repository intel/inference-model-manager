#
# Copyright (c) 2019 Intel Corporation
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

import pytest
import requests
import json

from config import DEFAULT_HEADERS, MODEL_MANAGEMENT_API_URL


@pytest.mark.parametrize("endpoint_fix, expected_status, expected_message",
                         [("endpoint_with_fake_model", 200, 'Models in {} tenant'),
                          ("tenant_with_endpoint", 200,
                           "There are no models present in {} tenant")])
def test_list_models(request, endpoint_fix, expected_status, expected_message):
    namespace, _ = request.getfixturevalue(endpoint_fix)
    url = MODEL_MANAGEMENT_API_URL.format(tenant_name=namespace)
    response = requests.get(url, headers=DEFAULT_HEADERS)
    assert expected_message.format(namespace) in response.text
    assert expected_status == response.status_code


@pytest.mark.parametrize("endpoint_fix, expected_status, expected_message",
                         [('fake_endpoint_with_fake_model', 200, 'Model deleted')])
def test_delete_model(request, endpoint_fix, expected_status, expected_message):
    namespace, body = request.getfixturevalue(endpoint_fix)
    model_name, model_version = body['spec']['modelName'], 1
    data = json.dumps({
        'modelName': model_name,
        'modelVersion': model_version
    })
    url = MODEL_MANAGEMENT_API_URL.format(tenant_name=namespace)
    response = requests.delete(url, data=data, headers=DEFAULT_HEADERS)
    model_path = f'{model_name}/{model_version}'
    assert expected_message.format(model_path) in response.text
    assert expected_status == response.status_code
