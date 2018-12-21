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

import pytest
import requests

from management_api_tests.config import DEFAULT_HEADERS, SERVINGS_MANAGEMENT_API_URL


@pytest.mark.skip
@pytest.mark.parametrize("crd, expected_status, expected_message",
                         [("crd_with_servings", 200, 'Servings in {}'),
                          ("crd_wo_servings", 200,
                           "There are no servings present in {}")])
def test_list_servings(request, crd, expected_status, expected_message):
    _, _ = request.getfixturevalue(crd)
    response = requests.get(SERVINGS_MANAGEMENT_API_URL, headers=DEFAULT_HEADERS)
    assert expected_message in response.text
    assert expected_status == response.status_code
