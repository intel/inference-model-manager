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

import os
from management_api.authenticate.auth_controller import get_auth_controller_url, get_token
from unittest.mock import Mock
import pytest


def test_get_auth_controller_url():
    os.environ["PLATFORM_DOMAIN"] = "example.com"
    url = get_auth_controller_url()
    assert url.startswith("https://dex.default")
    assert 'redirect_uri' in url and 'response_type' in url and 'client_id' in url


@pytest.mark.parametrize("case", [('fetch_token'), ('fetch_token_exc'), ('refresh_token'),
                                  ('refresh_token_exc')])
def test_get_token(mocker, case):
    oauth_session = Mock()
    create_custom_client_mock = mocker.patch('management_api.authenticate.auth_controller.'
                                             'OAuth2Session')
    create_custom_client_mock.return_value = oauth_session

    if case == 'fetch_token_exc':
        oauth_session.fetch_token.side_effect = Exception()
        with pytest.raises(Exception):
            get_token(parameters={'code': 'test'})
    elif case == 'fetch_token':
        returned_message = {'token': 'test'}
        oauth_session.fetch_token.return_value = returned_message
        output = get_token(parameters={'code': 'test'})
        assert returned_message == output
    elif case == 'refresh_token':
        returned_message = {'token': 'test'}
        oauth_session.refresh_token.return_value = returned_message
        output = get_token(parameters={'refresh_token': 'test'})
        assert returned_message == output
    else:
        oauth_session.refresh_token.side_effect = Exception()
        with pytest.raises(Exception):
            get_token(parameters={'refresh_token': 'test'})

    if 'refresh' in case:
        oauth_session.refresh_token.assert_called_once()
    else:
        oauth_session.fetch_token.assert_called_once()
    create_custom_client_mock.assert_called_once()
    create_custom_client_mock.assert_called_once()
