import pytest
import requests
import json

from management_api_tests.config import DEFAULT_HEADERS, ENDPOINT_MANAGEMENT_API_URL, CheckResult, \
    QUOTA_INCOMPLIANT_VALUES, ENDPOINT_RESOURCES, FAILING_UPDATE_PARAMS, FAILING_SCALE_PARAMS, \
    ENDPOINT_MANAGEMENT_API_URL_SCALE, ENDPOINT_MANAGEMENT_API_URL_UPDATE, OperationStatus
from management_api_tests.endpoints.endpoint_utils import check_replicas_number_matching_provided, \
    check_model_params_matching_provided, wait_server_setup, check_server_existence


def test_create_endpoint(function_context, apps_api_instance, get_k8s_custom_obj_client, tenant):
    headers = DEFAULT_HEADERS
    crd_server_name = 'predict'
    namespace, _ = tenant
    headers['Authorization'] = namespace
    replicas = 1
    data = json.dumps({
        'modelName': 'resnet',
        'modelVersion': 1,
        'endpointName': crd_server_name,
        'subjectName': 'client',
        'replicas': replicas,
        'resources': ENDPOINT_RESOURCES
    })
    url = ENDPOINT_MANAGEMENT_API_URL

    response = requests.post(url, data=data, headers=headers)

    assert response.status_code == 200
    assert "created" in response.text

    function_context.add_object(object_type='CRD', object_to_delete={'name': crd_server_name,
                                                                     'namespace': namespace})
    assert check_server_existence(get_k8s_custom_obj_client, namespace, crd_server_name
                                  ) == CheckResult.RESOURCE_AVAILABLE
    assert wait_server_setup(apps_api_instance, namespace, crd_server_name, replicas
                             ) == OperationStatus.SUCCESS


def test_delete_endpoint(tenant, apps_api_instance, get_k8s_custom_obj_client, endpoint):
    namespace, body = endpoint
    headers = DEFAULT_HEADERS
    headers['Authorization'] = namespace
    data = json.dumps({
        'endpointName': body['spec']['endpointName'],
    })

    url = ENDPOINT_MANAGEMENT_API_URL
    response = requests.delete(url, data=data, headers=headers)
    assert response.status_code == 200
    assert "deleted" in response.text
    assert check_server_existence(get_k8s_custom_obj_client, namespace, body['spec']['endpointName']
                                  ) == CheckResult.RESOURCE_DOES_NOT_EXIST
    assert wait_server_setup(apps_api_instance, namespace, body['spec']['endpointName'], 1
                             ) == OperationStatus.TERMINATED


def test_try_create_the_same_endpoint(tenant, endpoint):
    namespace, body = endpoint
    headers = DEFAULT_HEADERS
    body['spec']['resources'] = ENDPOINT_RESOURCES
    data = json.dumps(body['spec'])
    headers['Authorization'] = namespace

    url = ENDPOINT_MANAGEMENT_API_URL

    response = requests.post(url, data=data, headers=headers)
    assert response.status_code == 400
    assert "Conflict" in response.text


def test_create_endpoint_with_2_replicas(get_k8s_custom_obj_client, apps_api_instance,
                                         function_context, api_instance, tenant):
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
    assert "created" in response.text

    function_context.add_object(object_type='CRD', object_to_delete={'name': crd_server_name,
                                                                     'namespace': namespace})

    assert check_server_existence(get_k8s_custom_obj_client, namespace, crd_server_name
                                  ) == CheckResult.RESOURCE_AVAILABLE
    assert wait_server_setup(apps_api_instance, namespace, crd_server_name, replicas
                             ) == OperationStatus.SUCCESS


def test_scale_endpoint(get_k8s_custom_obj_client, api_instance, apps_api_instance,
                        tenant, endpoint):
    headers = DEFAULT_HEADERS
    namespace, body = endpoint
    headers['Authorization'] = namespace
    crd_server_name = body['spec']['endpointName']

    # -- scaling up 1 -> 5
    replicas = 5
    simulate_scaling(get_k8s_custom_obj_client, apps_api_instance, headers, namespace,
                     crd_server_name, replicas)

    # -- scaling down 5 -> 3
    replicas = 3
    simulate_scaling(get_k8s_custom_obj_client, apps_api_instance, headers, namespace,
                     crd_server_name, replicas)


def simulate_scaling(custom_obj_api, apps_api_instance, headers, namespace, name, replicas):

    url = ENDPOINT_MANAGEMENT_API_URL_SCALE.format(endpoint_name=name)
    headers['Authorization'] = namespace
    data = json.dumps({
        'replicas': replicas
    })

    response = requests.patch(url, data=data, headers=headers)

    assert response.status_code == 200
    assert "patched" in response.text
    assert check_replicas_number_matching_provided(
        custom_obj_api, namespace, name, provided_number=replicas
    ) == CheckResult.CONTENTS_MATCHING

    assert wait_server_setup(apps_api_instance, namespace, name, replicas
                             ) == OperationStatus.SUCCESS


@pytest.mark.parametrize("auth, endpoint_name, scale_params, expected_error",
                         FAILING_SCALE_PARAMS)
def test_not_scale_endpoint_bad_request(get_k8s_custom_obj_client, tenant,
                                        auth, endpoint_name, scale_params,
                                        expected_error, endpoint):
    headers = DEFAULT_HEADERS
    headers['Authorization'] = auth
    data = json.dumps(scale_params)

    url = ENDPOINT_MANAGEMENT_API_URL_SCALE.format(endpoint_name=endpoint_name)

    response = requests.patch(url, data=data, headers=headers)

    assert response.status_code == 400
    assert expected_error in response.text


def test_update_endpoint(get_k8s_custom_obj_client,
                         tenant, endpoint):
    headers = DEFAULT_HEADERS
    namespace, body = endpoint
    headers['Authorization'] = namespace
    crd_server_name = body['spec']['endpointName']
    new_values = {
        'modelName': 'super-model',
        'modelVersion': 3
    }
    data = json.dumps(new_values)

    url = ENDPOINT_MANAGEMENT_API_URL_UPDATE.format(endpoint_name=crd_server_name)

    response = requests.patch(url, data=data, headers=headers)

    assert response.status_code == 200
    assert "patched" in response.text
    assert check_model_params_matching_provided(
        get_k8s_custom_obj_client, namespace, crd_server_name, provided_params=new_values
    ) == CheckResult.CONTENTS_MATCHING


@pytest.mark.parametrize("auth, endpoint_name, update_params, expected_error",
                         FAILING_UPDATE_PARAMS)
def test_not_update_endpoint_bad_request(get_k8s_custom_obj_client, tenant,
                                         auth, endpoint_name, update_params, expected_error,
                                         endpoint):
    headers = DEFAULT_HEADERS
    headers['Authorization'] = auth

    data = json.dumps(update_params)

    url = ENDPOINT_MANAGEMENT_API_URL_UPDATE.format(endpoint_name=endpoint_name)

    response = requests.patch(url, data=data, headers=headers)

    assert response.status_code == 400
    assert expected_error in response.text


@pytest.mark.parametrize("incompliant_quota, expected_error", QUOTA_INCOMPLIANT_VALUES)
def test_not_create_endpoint_with_incompliant_resource_quota(tenant, incompliant_quota,
                                                             expected_error):
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
    assert expected_error in response.text
