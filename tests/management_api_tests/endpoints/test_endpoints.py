import pytest
import requests
import json

from management_api_tests.config import DEFAULT_HEADERS, USER1_HEADERS,\
    USER2_HEADERS, ENDPOINT_MANAGEMENT_API_URL, CheckResult, \
    ENDPOINT_RESOURCES, ENDPOINT_MANAGEMENT_API_URL_SCALE, \
    ENDPOINT_MANAGEMENT_API_URL_UPDATE, OperationStatus, CORRECT_UPDATE_QUOTAS, \
    ENDPOINT_MANAGEMENT_API_URL_VIEW

from management_api_tests.endpoints.endpoint_utils import check_replicas_number_matching_provided, \
    check_model_params_matching_provided, wait_server_setup, check_server_existence, \
    check_server_update_result


def test_create_endpoint(function_context, apps_api_instance, get_k8s_custom_obj_client,
                         session_tenant):
    crd_server_name = 'predict'
    namespace, _ = session_tenant
    replicas = 1
    data = json.dumps({
        'modelName': 'resnet',
        'modelVersion': 1,
        'endpointName': crd_server_name,
        'subjectName': 'client',
        'replicas': replicas,
        'resources': ENDPOINT_RESOURCES
    })
    url = ENDPOINT_MANAGEMENT_API_URL.format(tenant_name=namespace)

    response = requests.post(url, data=data, headers=DEFAULT_HEADERS)

    assert response.status_code == 200
    assert "created" in response.text

    function_context.add_object(object_type='CRD', object_to_delete={'name': crd_server_name,
                                                                     'namespace': namespace})
    assert check_server_existence(get_k8s_custom_obj_client, namespace, crd_server_name
                                  ) == CheckResult.RESOURCE_AVAILABLE
    assert wait_server_setup(apps_api_instance, namespace, crd_server_name, replicas
                             ) == OperationStatus.SUCCESS


def test_delete_endpoint(apps_api_instance, get_k8s_custom_obj_client,
                         tenant_with_endpoint):
    namespace, body = tenant_with_endpoint
    data = json.dumps({
        'endpointName': body['spec']['endpointName'],
    })

    url = ENDPOINT_MANAGEMENT_API_URL.format(tenant_name=namespace)
    response = requests.delete(url, data=data, headers=DEFAULT_HEADERS)
    assert response.status_code == 200
    assert "deleted" in response.text
    assert check_server_existence(get_k8s_custom_obj_client, namespace, body['spec']['endpointName']
                                  ) == CheckResult.RESOURCE_DOES_NOT_EXIST
    assert wait_server_setup(apps_api_instance, namespace, body['spec']['endpointName'], 1
                             ) == OperationStatus.TERMINATED


def test_try_create_the_same_endpoint(tenant_with_endpoint):
    namespace, body = tenant_with_endpoint
    body['spec']['resources'] = ENDPOINT_RESOURCES
    data = json.dumps(body['spec'])

    url = ENDPOINT_MANAGEMENT_API_URL.format(tenant_name=namespace)

    response = requests.post(url, data=data, headers=DEFAULT_HEADERS)
    assert response.status_code == 400
    assert "Conflict" in response.text


def test_create_endpoint_with_2_replicas(get_k8s_custom_obj_client, apps_api_instance,
                                         function_context, session_tenant):
    crd_server_name = 'predict'
    namespace, _ = session_tenant
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

    url = ENDPOINT_MANAGEMENT_API_URL.format(tenant_name=namespace)

    response = requests.post(url, data=data, headers=DEFAULT_HEADERS)

    assert response.status_code == 200
    assert "created" in response.text

    function_context.add_object(object_type='CRD', object_to_delete={'name': crd_server_name,
                                                                     'namespace': namespace})

    assert check_server_existence(get_k8s_custom_obj_client, namespace, crd_server_name
                                  ) == CheckResult.RESOURCE_AVAILABLE
    assert wait_server_setup(apps_api_instance, namespace, crd_server_name, replicas
                             ) == OperationStatus.SUCCESS


def test_scale_endpoint(get_k8s_custom_obj_client, apps_api_instance,
                        tenant_with_endpoint):
    headers = DEFAULT_HEADERS
    namespace, body = tenant_with_endpoint
    crd_server_name = body['spec']['endpointName']

    # -- scaling up 1 -> 5
    replicas = 5
    simulate_scaling(get_k8s_custom_obj_client, apps_api_instance, headers, namespace,
                     crd_server_name, replicas)

    # -- scaling down 5 -> 0
    replicas = 0
    simulate_scaling(get_k8s_custom_obj_client, apps_api_instance, headers, namespace,
                     crd_server_name, replicas)


def simulate_scaling(custom_obj_api, apps_api_instance, headers, namespace, name, replicas):
    url = ENDPOINT_MANAGEMENT_API_URL_SCALE.format(endpoint_name=name, tenant_name=namespace)
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


FAILING_SCALE_PARAMS = [
    (DEFAULT_HEADERS, "wrong_name", {'replicas': 3}, 400, "Not Found"),
    (DEFAULT_HEADERS, "predict", {'replicas': -1}, 400, "-1 is less than the minimum of 0"),
    (DEFAULT_HEADERS, "predict", {'replicas': "many"}, 400, "'many' is not of type 'integer'"),
    (DEFAULT_HEADERS, "predict", {}, 400, "{} is not valid under any of the given schemas"),
]


@pytest.mark.parametrize("auth, endpoint_name, scale_params, expected_status_code, "
                         "expected_error_msg",
                         FAILING_SCALE_PARAMS)
def test_fail_to_scale_endpoint(auth, tenant_with_endpoint, endpoint_name, scale_params,
                                expected_status_code, expected_error_msg):
    namespace, _ = tenant_with_endpoint
    data = json.dumps(scale_params)
    url = ENDPOINT_MANAGEMENT_API_URL_SCALE.format(endpoint_name=endpoint_name,
                                                   tenant_name=namespace)
    response = requests.patch(url, data=data, headers=auth)

    assert response.status_code == expected_status_code
    assert expected_error_msg in response.text


@pytest.mark.parametrize("new_values", CORRECT_UPDATE_QUOTAS)
def test_update_endpoint(get_k8s_custom_obj_client, apps_api_instance,
                         tenant_with_endpoint, new_values):
    namespace, body = tenant_with_endpoint
    crd_server_name = body['spec']['endpointName']
    data = json.dumps(new_values)

    url = ENDPOINT_MANAGEMENT_API_URL_UPDATE.format(endpoint_name=crd_server_name,
                                                    tenant_name=namespace)

    response = requests.patch(url, data=data, headers=DEFAULT_HEADERS)

    assert response.status_code == 200
    assert "patched" in response.text
    assert check_model_params_matching_provided(
        get_k8s_custom_obj_client, namespace, crd_server_name, provided_params=new_values
    ) == CheckResult.CONTENTS_MATCHING
    assert check_server_update_result(apps_api_instance, namespace, crd_server_name, new_values
                                      ) == CheckResult.CONTENTS_MATCHING


FAILING_UPDATE_PARAMS = [
    (DEFAULT_HEADERS, "wrong_name", {'modelName': 'super-model', 'modelVersion': 3}, 400,
     "Not Found"),
    (DEFAULT_HEADERS, "predict", {'modelName': 0, 'modelVersion': 3}, 400,
     "0 is not of type 'string'"),
    (DEFAULT_HEADERS, "predict", {'modelName': 'super-model', 'modelVersion': "str"}, 400,
     "'str' is not of type 'integer'"),
    (DEFAULT_HEADERS, "predict", {'modelVersion': 3}, 400, "{'modelVersion': 3} is not valid "
                                                           "under any of the given schemas"),
    (DEFAULT_HEADERS, "predict", {'modelName': 'super-model'}, 400,
     "{'modelName': 'super-model'} is not valid under any of the given schema"),
]


@pytest.mark.parametrize("auth, endpoint_name, update_params, expected_error_code, "
                         "expected_error_msg", FAILING_UPDATE_PARAMS)
def test_fail_to_update_endpoint(get_k8s_custom_obj_client,
                                 auth, endpoint_name, update_params,
                                 expected_error_code, expected_error_msg, tenant_with_endpoint):

    namespace, body = tenant_with_endpoint
    crd_server_name = body['spec']['endpointName']

    data = json.dumps(update_params)

    url = ENDPOINT_MANAGEMENT_API_URL_UPDATE.format(endpoint_name=endpoint_name,
                                                    tenant_name=namespace)

    response = requests.patch(url, data=data, headers=auth)

    assert response.status_code == expected_error_code
    assert expected_error_msg in response.text
    assert check_model_params_matching_provided(
        get_k8s_custom_obj_client, namespace, crd_server_name, provided_params=update_params
    ) == CheckResult.CONTENTS_MISMATCHING


QUOTA_INCOMPLIANT_VALUES = [
    ({}, "No resources provided"),
    ({'requests.cpu': '1'}, "Missing resources values"),
]


@pytest.mark.parametrize("incompliant_quota, expected_error", QUOTA_INCOMPLIANT_VALUES)
def test_not_create_endpoint_with_incompliant_resource_quota(session_tenant, incompliant_quota,
                                                             expected_error):

    crd_server_name = 'predict'
    namespace, _ = session_tenant

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

    url = ENDPOINT_MANAGEMENT_API_URL.format(tenant_name=namespace)

    headers = DEFAULT_HEADERS
    response = requests.post(url, data=data, headers=headers)

    assert response.status_code == 400
    assert expected_error in response.text


@pytest.mark.parametrize("tenant_fix, auth_headers, expected_status, expected_message",
                         [('tenant_with_endpoint', DEFAULT_HEADERS, 200,
                           "Endpoints present in {} tenant"),
                          ('empty_tenant', DEFAULT_HEADERS, 200,
                           "There's no endpoints present in {} tenant"),
                          ('fake_tenant_endpoint', USER1_HEADERS, 404, "Tenant {} does not exist")
                          ])
def test_list_endpoints(request, tenant_fix, auth_headers,
                        expected_status, expected_message):
    namespace, _ = request.getfixturevalue(tenant_fix)
    url = ENDPOINT_MANAGEMENT_API_URL.format(tenant_name=namespace)
    response = requests.get(url, headers=auth_headers)

    assert expected_status == response.status_code
    assert expected_message.format(namespace) in response.text


@pytest.mark.parametrize("endpoint_fix, endpoint_name, expected_status, expected_message",
                         [('tenant_with_endpoint', 'predict', 200, "Endpoint {} in {} tenant"),
                          ('tenant_with_endpoint', 'not_exist', 404, 'Endpoint {} does not exist')])
def test_view_endpoint(request, endpoint_fix, endpoint_name, expected_status, expected_message):
    namespace, _ = request.getfixturevalue(endpoint_fix)
    url = ENDPOINT_MANAGEMENT_API_URL_VIEW.format(endpoint_name=endpoint_name,
                                                  tenant_name=namespace)
    response = requests.get(url, headers=DEFAULT_HEADERS)

    assert expected_status == response.status_code
    assert expected_message.format(endpoint_name, namespace) in response.text


def test_not_create_endpoint_tenant_not_exist():
    headers = USER2_HEADERS
    crd_server_name = 'predict'
    namespace = 'janusz'
    replicas = 1
    data = json.dumps({
        'modelName': 'resnet',
        'modelVersion': 1,
        'endpointName': crd_server_name,
        'subjectName': 'client',
        'replicas': replicas,
        'resources': ENDPOINT_RESOURCES
    })
    url = ENDPOINT_MANAGEMENT_API_URL.format(tenant_name=namespace)

    response = requests.post(url, data=data, headers=headers)

    assert response.status_code == 404
    assert "Tenant {} does not exist".format(namespace) in response.text
