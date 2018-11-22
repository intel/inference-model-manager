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
import falcon


@pytest.mark.parametrize("tenant_exists, expected_status",
                         [(True, falcon.HTTP_OK),
                          (False, falcon.HTTP_404)])
def test_multipart_start(client, mocker, tenant_exists, expected_status):
    body = {'modelName': 'test', 'modelVersion': 3, 'fileName': 'filename'}
    upload_id = 'test'
    tenant_existence_mock = mocker.patch('management_api.upload.multipart.tenant_exists')
    tenant_existence_mock.return_value = tenant_exists
    upload_id_mock = mocker.patch('management_api.upload.multipart.create_upload')
    upload_id_mock.return_value = upload_id
    result = client.simulate_request(method='POST', path='/tenants/default/upload/start',
                                     headers={},
                                     json=body)
    assert expected_status == result.status
    tenant_existence_mock.assert_called_once()
    if tenant_exists:
        upload_id_mock.upload_id_mock()


@pytest.mark.parametrize("tenant_exists, expected_status",
                         [(True, falcon.HTTP_OK),
                          (False, falcon.HTTP_404)])
def test_multipart_write(client, mocker, tenant_exists, expected_status):
    tenant_existence_mock = mocker.patch('management_api.upload.multipart.tenant_exists')
    tenant_existence_mock.return_value = tenant_exists
    upload_part_mock = mocker.patch('management_api.upload.multipart.upload_part')
    upload_part_mock.return_value = 'part_etag'
    result = client.simulate_request(method='PUT',
                                     path='/tenants/default/upload',
                                     params={'partNumber': '1',
                                             'uploadId': 'some-id',
                                             'modelName': 'model',
                                             'modelVersion': '1',
                                             'fileName': 'filename'},
                                     headers={})
    assert expected_status == result.status
    tenant_existence_mock.assert_called_once()
    if tenant_exists:
        upload_part_mock.upload_part_mock()


@pytest.mark.parametrize("tenant_exists, expected_status",
                         [(True, falcon.HTTP_OK),
                          (False, falcon.HTTP_404)])
def test_multipart_done(client, mocker, tenant_exists, expected_status):
    body = {'modelName': 'test', 'modelVersion': 3, 'fileName': 'filename',
            'uploadId': 'some-id', 'parts': []}
    tenant_existence_mock = mocker.patch('management_api.upload.multipart.tenant_exists')
    tenant_existence_mock.return_value = tenant_exists
    complete_upload_mock = mocker.patch('management_api.upload.multipart.complete_upload')
    result = client.simulate_request(method='POST', path='/tenants/default/upload/done',
                                     headers={},
                                     json=body)
    assert expected_status == result.status
    tenant_existence_mock.assert_called_once()
    if tenant_exists:
        complete_upload_mock.complete_upload_mock()


@pytest.mark.parametrize("tenant_exists, expected_status",
                         [(True, falcon.HTTP_OK),
                          (False, falcon.HTTP_404)])
def test_multipart_abort(client, mocker, tenant_exists, expected_status):
    body = {'modelName': 'test', 'modelVersion': 3, 'fileName': 'filename',
            'uploadId': 'some-id'}
    tenant_existence_mock = mocker.patch('management_api.upload.multipart.tenant_exists')
    tenant_existence_mock.return_value = tenant_exists
    abort_upload_mock = mocker.patch('management_api.upload.multipart.abort_upload')
    result = client.simulate_request(method='POST', path='/tenants/default/upload/abort',
                                     headers={},
                                     json=body)
    assert expected_status == result.status
    tenant_existence_mock.assert_called_once()
    if tenant_exists:
        abort_upload_mock.complete_upload_mock()
