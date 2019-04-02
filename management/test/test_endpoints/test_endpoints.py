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
import json

CREATED_MESSAGE = '"status": "CREATED"'


@pytest.mark.parametrize("body, expected_message, expected_status, model_availability",
                         [({'modelName': 'test', 'modelVersionPolicy':
                            '{latest{}}', 'endpointName': 'test', 'subjectName': 'test',
                            'servingName': 'test'}, CREATED_MESSAGE, falcon.HTTP_OK, True),
                          ({'modelName': 'test', 'endpointName': 'test', 'subjectName': 'test',
                            'servingName': 'test'}, CREATED_MESSAGE, falcon.HTTP_OK, True),
                          ({'modelName': 'test', 'endpointName': 'test', 'subjectName': 'test',
                            'servingName': 'test'}, CREATED_MESSAGE, falcon.HTTP_OK, False),
                          ({'modelName': 'test', 'modelVersionPolicy':
                              '{ all { } }', 'endpointName': 'test', 'subjectName': 'test',
                            'servingName': 'test', 'resources': {'requests.cpu': '1'}},
                           CREATED_MESSAGE, falcon.HTTP_OK, True),
                          ({'modelName': 'test', 'modelVersionPolicy':
                              'specific {versions: 3}}', 'endpointName': 'test',
                            'subjectName': 'test', 'servingName': 'test'}, 'Failed data validation',
                           falcon.HTTP_BAD_REQUEST, True),
                          ({'modelName': 'test', 'modelVersionPolicy':
                              1, 'endpointName': 'test',
                            'subjectName': 'test', 'servingName': 'test'}, 'Failed data validation',
                           falcon.HTTP_BAD_REQUEST, True)])
def test_endpoints_post(mocker, client, body, expected_message, expected_status,
                        model_availability):
    create_endpoint_mock = mocker.patch('management_api.endpoints.endpoints.create_endpoint')
    create_endpoint_mock.return_value = "test"
    check_model_mock = mocker.patch('management_api.endpoints.endpoints.check_endpoint_model')
    check_model_mock.return_value = model_availability

    result = client.simulate_request(method='POST', path='/tenants/default/endpoints', headers={},
                                     json=body)
    assert expected_status == result.status
    assert expected_message in result.text
    if not model_availability:
        assert "test model is not available on the platform" in result.text
    if result.status == falcon.HTTP_OK:
        create_endpoint_mock.assert_called_once()


def test_endpoints_delete(mocker, client):
    delete_endpoint_mock = mocker.patch('management_api.endpoints.endpoints.delete_endpoint')
    delete_endpoint_mock.return_value = "test"
    expected_status = falcon.HTTP_OK
    expected_message = {"status": "DELETED", "data": {"url": "test"}}
    body = {'endpointName': 'test'}

    result = client.simulate_request(method='DELETE', path='/tenants/default/endpoints', headers={},
                                     json=body)
    assert expected_status == result.status
    assert expected_message == json.loads(result.text)
    delete_endpoint_mock.assert_called_once()


@pytest.mark.parametrize("functionality, method_name, body, expected_message, expected_status",
                         [("replicas", "scale_endpoint", {'replicas': 3},
                           '{"status": "PATCHED", "data": {"url": "test", '
                           '"values": {"replicas": 3}}}',
                          falcon.HTTP_OK),
                          ("", "update_endpoint",
                           {'modelName': 'test', 'modelVersionPolicy': '{specific {versions: 3}}'},
                           '{"status": "PATCHED", "data": {"url": "test", "values": {"modelName": '
                           '"test", "modelVersionPolicy": "{specific {versions: 3}}"}}}',
                           falcon.HTTP_OK),
                          ("", "update_endpoint", {'modelName': 'test'},
                           '{"status": "PATCHED", "data": {"url": "test", "values": {"modelName": '
                           '"test"}}}',
                           falcon.HTTP_OK),
                          ("", "update_endpoint",
                           {'modelName': 'test', 'modelVersionPolicy': '1,2'},
                           'Failed data validation', falcon.HTTP_BAD_REQUEST),
                          ("", "update_endpoint",
                           {'modelVersionPolicy': 'latest'},
                           'Failed data validation', falcon.HTTP_BAD_REQUEST),
                          ])
def test_endpoints_patch(mocker, client, functionality, method_name, body, expected_message,
                         expected_status):
    method_mock = mocker.patch('management_api.endpoints.endpoints.' + method_name)
    method_mock.return_value = "test"

    result = client.simulate_request(method='PATCH', path=f'/tenants/default/endpoints/test/'
                                                          f'{functionality}',
                                     headers={}, json=body)
    assert expected_status == result.status
    assert expected_message in result.text
    if result.status == falcon.HTTP_OK:
        method_mock.assert_called_once()


@pytest.mark.parametrize("functionality, method_name, expected_status, expected_message",
                         [("", "list_endpoints", falcon.HTTP_OK,
                           {"status": "OK", "data": {"endpoints": "test"}}),
                          ("/predict", "view_endpoint", falcon.HTTP_OK,
                           {"status": "OK", "data": {"url": "test"}})])
def test_endpoints_get(mocker, client, functionality, method_name,
                       expected_status, expected_message):
    namespace = 'test'
    header = {'Authorization': namespace}
    get_endpoint_mock = mocker.patch('management_api.endpoints.endpoints.' + method_name)
    get_endpoint_mock.return_value = namespace

    result = client.simulate_request(method='GET', path=f'/tenants/{namespace}/endpoints'
                                                        f'{functionality}',
                                     headers=header)

    assert expected_status == result.status
    assert expected_message == json.loads(result.text)
    get_endpoint_mock.assert_called_once()
