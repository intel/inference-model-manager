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

import pytest
import falcon


@pytest.mark.parametrize("params, expected_redirect_url", [({'offline': True}, 'oob'),
                                                           ({}, 'callback')])
def test_authenticate_get(client, params, expected_redirect_url):
    expected_status = falcon.HTTP_308
    result = client.simulate_request(method='GET', path='/authenticate', params=params)
    assert expected_status == result.status
    assert expected_redirect_url in result.headers['Location']


@pytest.mark.parametrize("body, expected_status",
                         [({'code': 'test'}, falcon.HTTP_OK),
                          ({'modelName': 'wrong'}, falcon.HTTP_400),
                          ({'refresh_token': 'test'}, falcon.HTTP_OK)])
def test_token_post(mocker, client, body, expected_status):
    get_token_mock = mocker.patch('management_api.authenticate.authenticate.get_token')
    get_token_mock.return_value = "test"
    result = client.simulate_request(method='POST', json=body, path='/authenticate/token')
    assert expected_status == result.status
    if expected_status is falcon.HTTP_OK:
        get_token_mock.assert_called_once()
        assert 'token' in result.text
