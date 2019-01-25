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

import requests
import pytest
import json

from config import AUTH_MANAGEMENT_API_URL, TOKEN_MANAGEMENT_API_URL
from management_api_tests.authenticate import authenticate, MERCURY_CREDENTIALS


def test_get_auth_redirection():
    url = AUTH_MANAGEMENT_API_URL
    response = requests.get(url, allow_redirects=False)
    assert response.status_code == 308


@pytest.mark.parametrize("body_key, refresh_token", [('code', False), ('refresh_token', True)])
def test_get_token(body_key, refresh_token):
    if 'code' in body_key:
        code = authenticate(username=MERCURY_CREDENTIALS['login'],
                            password=MERCURY_CREDENTIALS['password'],
                            token=refresh_token)
    else:
        code = authenticate(username=MERCURY_CREDENTIALS['login'],
                            password=MERCURY_CREDENTIALS['password'],
                            token=refresh_token)['refresh_token']
    url = TOKEN_MANAGEMENT_API_URL
    data = json.dumps({
        body_key: code
    })
    response = requests.post(url, data=data)

    assert response.status_code == 200
    assert 'token' in response.text
