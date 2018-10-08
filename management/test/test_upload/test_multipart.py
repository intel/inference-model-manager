import pytest
import falcon


@pytest.mark.parametrize("tenant_exists, expected_status",
                         [(True, falcon.HTTP_OK),
                          (False, falcon.HTTP_404)])
def test_multipart_start(client, mocker, tenant_exists, expected_status):
    body = {'modelName': 'test', 'modelVersion': 3}
    upload_id = 'test'
    tenant_existence_mock = mocker.patch('management_api.upload.multipart.tenant_exists')
    tenant_existence_mock.return_value = tenant_exists
    upload_id_mock = mocker.patch('management_api.upload.multipart.create_upload')
    upload_id_mock.return_value = upload_id
    result = client.simulate_request(method='POST', path='/upload/start', headers={},
                                     json=body)
    assert expected_status == result.status
    tenant_existence_mock.assert_called_once()
    if tenant_exists:
        upload_id_mock.upload_id_mock()


@pytest.mark.parametrize("tenant_exists, expected_status",
                         [(True, falcon.HTTP_OK),
                          (False, falcon.HTTP_404)])
def test_multipart_write(client, mocker, tenant_exists, expected_status):
    header = {'Authorization': 'default'}
    tenant_existence_mock = mocker.patch('management_api.upload.multipart.tenant_exists')
    tenant_existence_mock.return_value = tenant_exists
    upload_part_mock = mocker.patch('management_api.upload.multipart.upload_part')
    result = client.simulate_request(method='PUT',
                                     path='/upload',
                                     params={'partNumber': '1',
                                             'uploadId': 'some-id',
                                             'modelName': 'model',
                                             'modelVersion': '1'},
                                     headers=header)
    assert expected_status == result.status
    tenant_existence_mock.assert_called_once()
    if tenant_exists:
        upload_part_mock.upload_part_mock()


@pytest.mark.parametrize("tenant_exists, expected_status",
                         [(True, falcon.HTTP_OK),
                          (False, falcon.HTTP_404)])
def test_multipart_done(client, mocker, tenant_exists, expected_status):
    header = {'Authorization': 'default'}
    body = {'modelName': 'test', 'modelVersion': 3, 'multipartId': 'some-id'}
    tenant_existence_mock = mocker.patch('management_api.upload.multipart.tenant_exists')
    tenant_existence_mock.return_value = tenant_exists
    complete_upload_mock = mocker.patch('management_api.upload.multipart.complete_upload')
    result = client.simulate_request(method='POST', path='/upload/done', headers=header,
                                     json=body)
    assert expected_status == result.status
    tenant_existence_mock.assert_called_once()
    if tenant_exists:
        complete_upload_mock.complete_upload_mock()
