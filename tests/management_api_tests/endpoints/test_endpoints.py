import requests
import json
from management_api_tests.config import DEFAULT_HEADERS, MANAGEMENT_API_URL
from management_api_tests.endpoints.endpoint_utils import is_replicas_number_correct
from conftest import create_default_endpoint, delete_default_endpoint

url = MANAGEMENT_API_URL + '/endpoint'


def test_scale_endpoint(custom_obj_api_instance):
    create_default_endpoint()
    headers = DEFAULT_HEADERS
    crd_server_name = 'predict'
    namespace = 'default'
    headers['Authorization'] = namespace
    data = json.dumps({
        'endpointName': crd_server_name,
        'replicas': 10
    })

    response = requests.patch(url, data=data, headers=headers)
    assert response.status_code == 200
    assert is_replicas_number_correct(custom_obj_api_instance, namespace, crd_server_name,
                                      expected_amount=10)
    delete_default_endpoint()

