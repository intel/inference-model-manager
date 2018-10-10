import falcon


def test_models_delete(mocker, client):
    delete_model_mock = mocker.patch('management_api.models.models.delete_model')
    delete_model_mock.return_value = 'test'
    header = {'Authorization': 'default'}
    body = {'modelName': 'test', 'modelVersion': 1}
    expected_status = falcon.HTTP_OK

    result = client.simulate_request(method='DELETE', path='/models', headers=header, json=body)

    assert expected_status == result.status
    delete_model_mock.assert_called_once()
