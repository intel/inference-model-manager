import pytest
import falcon


@pytest.mark.parametrize("body, expected_status",
                         [({'modelName': 'test', 'modelVersion': 3, 'endpointName': 'test',
                           'subjectName': 'test'}, falcon.HTTP_OK),
                          ({'modelName': 'test', 'modelVersion': 3, 'endpointName': 'test',
                           'subjectName': 'test', 'resources': {'requests.cpu': '1'}},
                           falcon.HTTP_OK)])
def test_endpoints_post(mocker, client, body, expected_status):
    create_endpoint_mock = mocker.patch('management_api.endpoints.endpoints.create_endpoint')
    create_endpoint_mock.return_value = "test"
    header = {'Authorization': 'default'}
    expected_message = 'Endpoint created\n {}'.format("test")

    result = client.simulate_request(method='POST', path='/endpoint', headers=header, json=body)
    assert expected_status == result.status
    assert expected_message == result.text
    create_endpoint_mock.assert_called_once()


def test_endpoints_delete(mocker, client):
    delete_endpoint_mock = mocker.patch('management_api.endpoints.endpoints.delete_endpoint')
    delete_endpoint_mock.return_value = "test"
    external_address_mock = mocker.patch('management_api.endpoints.endpoints.create_url_to_service')
    external_address_mock.return_value = {"test": "test"}
    header = {'Authorization': 'default'}
    expected_status = falcon.HTTP_OK
    body = {'endpointName': 'test'}

    result = client.simulate_request(method='DELETE', path='/endpoint', headers=header, json=body)
    assert expected_status == result.status
    delete_endpoint_mock.assert_called_once()
