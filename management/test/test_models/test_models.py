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

import falcon


def test_models_get(mocker, client):
    list_models_mock = mocker.patch('management_api.models.models.list_models')
    list_models_mock.return_value = 'test'
    expected_status = falcon.HTTP_OK

    result = client.simulate_request(method='GET', path='/tenants/default/models', headers={})

    assert expected_status == result.status
    list_models_mock.assert_called_once()


def test_models_delete(mocker, client):
    delete_model_mock = mocker.patch('management_api.models.models.delete_model')
    delete_model_mock.return_value = 'test'
    body = {'modelName': 'test', 'modelVersion': 1}
    expected_status = falcon.HTTP_OK

    result = client.simulate_request(method='DELETE', path='/tenants/default/models',
                                     headers={},
                                     json=body)

    assert expected_status == result.status
    delete_model_mock.assert_called_once()
