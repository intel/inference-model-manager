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
