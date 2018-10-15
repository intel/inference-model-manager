import pytest
import requests
import json

from management_api_tests.config import DEFAULT_HEADERS, MODEL_MANAGEMENT_API_URL


@pytest.mark.parametrize("endpoint_fix, expected_status, expected_message",
                         [('fake_endpoint_with_empty_model', 200, 'Model {} deleted'),
                          ('endpoint_with_empty_model', 409, 'Model delete error')])
def test_delete_model(request, endpoint_fix, expected_status, expected_message):
    namespace, body = request.getfixturevalue(endpoint_fix)
    model_name, model_version = body['spec']['modelName'], body['spec']['modelVersion']
    data = json.dumps({
        'modelName': model_name,
        'modelVersion': model_version
    })
    model_path = f'{model_name}-{model_version}'
    url = MODEL_MANAGEMENT_API_URL

    response = requests.delete(url, data=data, headers=DEFAULT_HEADERS)

    assert expected_status == response.status_code
    assert expected_message.format(model_path) in response.text
