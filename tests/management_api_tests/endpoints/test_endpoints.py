import pytest
import requests
import json

from conftest import get_all_pods_in_namespace
from management_api_tests.config import DEFAULT_HEADERS, ENDPOINT_MANAGEMENT_API_URL, CheckResult, \
                                        QUOTA_INCOMPLIANT_VALUES, ENDPOINT_RESOURCES
from management_api_tests.endpoints.endpoint_utils import check_replicas_number_matching_provided


def test_create_endpoint(function_context, tenant):
    headers = DEFAULT_HEADERS
    crd_server_name = 'predict'
    namespace, _ = tenant
    headers['Authorization'] = namespace
    data = json.dumps({
        'modelName': 'resnet',
        'modelVersion': 1,
        'endpointName': crd_server_name,
        'subjectName': 'client',
        'replicas': 1,
        'resources': ENDPOINT_RESOURCES
    })
    url = ENDPOINT_MANAGEMENT_API_URL

    response = requests.post(url, data=data, headers=headers)

    assert response.status_code == 200

    function_context.add_object(object_type='CRD', object_to_delete={'name': crd_server_name,
                                                                     'namespace': namespace})


def test_delete_endpoint(tenant, endpoint):
    namespace, body = endpoint
    headers = DEFAULT_HEADERS
    headers['Authorization'] = namespace
    data = json.dumps({
        'endpointName': body['spec']['endpointName'],
    })

    url = ENDPOINT_MANAGEMENT_API_URL
    response = requests.delete(url, data=data, headers=headers)
    assert response.status_code == 200
    

def test_try_create_the_same_endpoint(tenant, endpoint):
    namespace, body = endpoint
    headers = DEFAULT_HEADERS
    data = json.dumps(body)
    headers['Authorization'] = namespace

    url = ENDPOINT_MANAGEMENT_API_URL

    response = requests.post(url, data=data, headers=headers)
    assert response.status_code == 400
   

def test_create_endpoint_with_2_replicas(function_context, api_instance, tenant):
    headers = DEFAULT_HEADERS
    crd_server_name = 'predict'
    namespace, _ = tenant
    headers['Authorization'] = namespace
    model_name = 'resnet2'
    model_version = 1
    replicas = 2
    data = json.dumps({
        'modelName': model_name,
        'modelVersion': model_version,
        'endpointName': crd_server_name,
        'subjectName': 'client',
        'replicas': replicas,
        'resources': ENDPOINT_RESOURCES
    })

    url = ENDPOINT_MANAGEMENT_API_URL

    response = requests.post(url, data=data, headers=headers)

    assert response.status_code == 200

    function_context.add_object(object_type='CRD', object_to_delete={'name': crd_server_name,
                                                                     'namespace': namespace})
    pod_id = '{}-{}'.format(model_name, model_version)
    label_selector = 'endpoint={},id={}'.format(crd_server_name, pod_id)
    pods = get_all_pods_in_namespace(k8s_client=api_instance, namespace=namespace,
                                     label_selector=label_selector)

    assert replicas == len(pods.items)
 

def test_scale_endpoint(function_context, get_k8s_custom_obj_client,
                        tenant, endpoint):
    headers = DEFAULT_HEADERS
    namespace, body = endpoint
    headers['Authorization'] = namespace
    crd_server_name = body['spec']['endpointName']
    data = json.dumps({
        'endpointName': crd_server_name,
        'replicas': 10
    })

    url = ENDPOINT_MANAGEMENT_API_URL

    response = requests.patch(url, data=data, headers=headers)

    assert response.status_code == 200
    assert check_replicas_number_matching_provided(
        get_k8s_custom_obj_client, namespace, crd_server_name, provided_number=10
    ) == CheckResult.CONTENTS_MATCHING


@pytest.mark.parametrize("incompliant_quota, expected_error", QUOTA_INCOMPLIANT_VALUES)
def test_not_create_endpoint_with_incompliant_resource_quota(tenant,
                                                    incompliant_quota, expected_error):
    headers = DEFAULT_HEADERS
    crd_server_name = 'predict'
    namespace, _ = tenant
    headers['Authorization'] = namespace
    model_name = 'resnet'
    model_version = 1
    replicas = 1
    data = json.dumps({
        'modelName': model_name,
        'modelVersion': model_version,
        'endpointName': crd_server_name,
        'subjectName': 'client',
        'replicas': replicas,
        'resources': incompliant_quota
    })

    url = ENDPOINT_MANAGEMENT_API_URL

    response = requests.post(url, data=data, headers=headers)
    
    assert response.status_code == 400
    assert response.text == expected_error
