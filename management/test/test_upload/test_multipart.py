import pytest
import falcon
from management_api.utils.errors_handling import TenantDoesNotExistException


@pytest.mark.parametrize("tenant_exists, expected_status",
                         [(True, falcon.HTTP_OK),
                          (False, falcon.HTTP_404)])
def test_multipart_start(client, mocker, tenant_exists, expected_status):
    header = {'Authorization': 'default'}
    body = {'modelName': 'test', 'modelVersion': 3}
    upload_id = 'test'
    tenant_existence_mock = mocker.patch('management_api.upload.multipart.tenant_exists')
    tenant_existence_mock.return_value = tenant_exists
    upload_id_mock = mocker.patch('management_api.upload.multipart.create_upload')
    upload_id_mock.return_value = upload_id
    result = client.simulate_request(method='POST', path='/upload/start', headers=header,
                                     json=body)
    assert expected_status == result.status
    tenant_existence_mock.assert_called_once()
    if tenant_exists:
        upload_id_mock.upload_id_mock()
