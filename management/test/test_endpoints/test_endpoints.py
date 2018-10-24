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
    expected_message = 'Endpoint created\n {}'.format("test")

    result = client.simulate_request(method='POST', path='/tenants/default/endpoints', headers={},
                                     json=body)
    assert expected_status == result.status
    assert expected_message == result.text
    create_endpoint_mock.assert_called_once()


def test_endpoints_delete(mocker, client):
    delete_endpoint_mock = mocker.patch('management_api.endpoints.endpoints.delete_endpoint')
    delete_endpoint_mock.return_value = "test"
    expected_status = falcon.HTTP_OK
    body = {'endpointName': 'test'}

    result = client.simulate_request(method='DELETE', path='/tenants/default/endpoints', headers={},
                                     json=body)
    assert expected_status == result.status
    delete_endpoint_mock.assert_called_once()


@pytest.mark.parametrize("functionality, method_name, body, expected_status",
                         [("scaling", "scale_endpoint", {'replicas': 3}, falcon.HTTP_OK),
                          ("updating", "update_endpoint", {'modelName': 'test', 'modelVersion': 3},
                           falcon.HTTP_OK)])
def test_endpoints_patch(mocker, client, functionality, method_name, body, expected_status):
    method_mock = mocker.patch('management_api.endpoints.endpoints.' + method_name)
    method_mock.return_value = "test"
    expected_message = 'patched successfully'

    result = client.simulate_request(method='PATCH', path=f'/tenants/default/endpoints/test/'
                                                          f'{functionality}',
                                     headers={}, json=body)
    assert expected_status == result.status
    assert expected_message in result.text
    method_mock.assert_called_once()


@pytest.mark.parametrize("functionality, method_name, expected_status, expected_message",
                         [("", "list_endpoints", falcon.HTTP_OK,
                           "There's no endpoints presented in {0} tenant"),
                          ("/predict/viewing", "view_endpoint", falcon.HTTP_OK,
                           "Endpoint {1} in {0} tenant")])
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
    assert result.text in expected_message.format(namespace, "predict")
    get_endpoint_mock.assert_called_once()
