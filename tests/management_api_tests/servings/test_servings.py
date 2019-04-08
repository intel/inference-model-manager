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

from config import ADMIN_HEADERS, SERVINGS_MANAGEMENT_API_URL, SERVING_MANAGEMENT_API_URL


@pytest.mark.parametrize("expected_status, expected_message",
                         [(200, {"status": "OK", "data": ["ovms", "tf-serving"]})])
def test_list_servings(expected_status, expected_message):
    response = requests.get(SERVINGS_MANAGEMENT_API_URL,
                            headers=ADMIN_HEADERS)
    assert expected_message == json.loads(response.text)
    assert expected_status == response.status_code


@pytest.mark.parametrize("serving_name, expected_status, expected_message",
                         [('tf-serving', 200, ['configMap.tmpl', 'deployment.tmpl', 'ingress.tmpl',
                                               'service.tmpl']),
                          ('ovms', 200, ['configMap.tmpl', 'deployment.tmpl', 'ingress.tmpl',
                                         'service.tmpl'])])
def test_view_serving(serving_name, expected_status, expected_message):
    url = SERVING_MANAGEMENT_API_URL.format(serving_name=serving_name)
    response = requests.get(url, headers=ADMIN_HEADERS)
    assert expected_status == response.status_code
    for i in expected_message:
        assert i in response.text


@pytest.mark.parametrize("non_existing_serving_name, expected_status, expected_message",
                         [('non-existing-serving-name', 400,
                           'An error occurred during reading config map object')])
def test_failure_on_view_non_existing_serving(non_existing_serving_name, expected_status,
                                              expected_message):
    url = SERVING_MANAGEMENT_API_URL.format(serving_name=non_existing_serving_name)
    response = requests.get(url, headers=ADMIN_HEADERS)
    assert expected_status == response.status_code
    assert expected_message in response.text
