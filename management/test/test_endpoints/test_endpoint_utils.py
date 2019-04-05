#
# Copyright (c) 2018 Intel Corporation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

from management_api.endpoints.endpoint_utils import create_endpoint, delete_endpoint, \
    create_url_to_service, update_endpoint, scale_endpoint, list_endpoints, view_endpoint
from kubernetes.client.rest import ApiException
import pytest
from unittest.mock import Mock

from test_utils.token_stuff import user_token

from management_api.utils.errors_handling import KubernetesCreateException, \
    KubernetesDeleteException, KubernetesUpdateException, KubernetesGetException, \
    TenantDoesNotExistException, EndpointDoesNotExistException


@pytest.mark.parametrize("tenant_exception, raise_error", [(True, False), (False, True)])
def test_create_endpoint(mocker, url_to_service_endpoint_utils,
                         custom_client_mock_endpoint_utils, tenant_exception,
                         raise_error, api_client_mock_endpoint_utils,
                         apps_client_mock_endpoint_utils):
    tenant_exists_mock = mocker.patch(
        'management_api.endpoints.endpoint_utils.tenant_exists')
    if tenant_exception:
        with pytest.raises(TenantDoesNotExistException):
            tenant_exists_mock.return_value = False
            create_endpoint(parameters={'endpointName': "test", 'resources': {}}, namespace="test",
                            id_token=user_token)
    ing_ip_mock, ing_ip_mock_return_values = url_to_service_endpoint_utils
    create_custom_client_mock, custom_client = custom_client_mock_endpoint_utils
    create_apps_client_mock, apps_client = apps_client_mock_endpoint_utils
    verify_endpoint_amount_mock = mocker.patch(
         'management_api.endpoints.endpoint_utils.verify_endpoint_amount')
    verify_endpoint_amount_mock.return_value = None
    validate_quota_compliance_mock = mocker.patch(
        'management_api.endpoints.endpoint_utils.validate_quota_compliance')
    parameters_resources_mock = mocker.patch(
        'management_api.endpoints.endpoint_utils.transform_quota')
    if raise_error:
        with pytest.raises(KubernetesCreateException):
            custom_client.create_namespaced_custom_object.side_effect = ApiException()
            create_endpoint(parameters={'endpointName': "test", 'resources': {}}, namespace="test",
                            id_token=user_token)
    else:
        tenant_exists_mock.return_value = True
        create_endpoint(parameters={'endpointName': "test", 'resources': {}}, namespace="test",
                        id_token=user_token)
        ing_ip_mock.assert_called_once()

    validate_quota_compliance_mock.assert_called_once()
    parameters_resources_mock.assert_called_once()
    custom_client.create_namespaced_custom_object.assert_called_once()


@pytest.mark.parametrize("raise_error", [(False), (True)])
def test_delete_endpoint(custom_client_mock_endpoint_utils,
                         url_to_service_endpoint_utils, raise_error):
    ing_ip_mock, ing_ip_mock_return_values = url_to_service_endpoint_utils
    create_custom_client_mock, custom_client = custom_client_mock_endpoint_utils

    if raise_error:
        with pytest.raises(KubernetesDeleteException):
            custom_client.delete_namespaced_custom_object.side_effect = ApiException()
            delete_endpoint(parameters={'endpointName': 'test'}, namespace="test",
                            id_token=user_token)
    else:
        delete_endpoint(parameters={'endpointName': 'test'}, namespace="test",
                        id_token=user_token)
        ing_ip_mock.assert_called_once()
    custom_client.delete_namespaced_custom_object.assert_called_once()
    create_custom_client_mock.assert_called_once()


call_data = [(scale_endpoint, {'replicas': 2}),
             (update_endpoint, {'modelName': 'test',
                                'modelVersionPolicy': '{specific {versions: 2}}'})]


@pytest.mark.parametrize("method, arguments", call_data)
def test_read_endpoint_fail(custom_client_mock_endpoint_utils, api_client_mock_endpoint_utils,
                            url_to_service_endpoint_utils, method, arguments):
    ing_ip_mock, ing_ip_mock_return_values = url_to_service_endpoint_utils
    create_custom_client_mock, custom_client = custom_client_mock_endpoint_utils
    with pytest.raises(KubernetesGetException):
        custom_client.get_namespaced_custom_object.side_effect = ApiException()
        method(parameters=arguments, namespace="test", endpoint_name="test",
               id_token=user_token)
    create_custom_client_mock.assert_called_once()
    custom_client.get_namespaced_custom_object.assert_called_once()


@pytest.mark.parametrize("method, arguments", call_data)
def test_patch_endpoint_fail(custom_client_mock_endpoint_utils,
                             url_to_service_endpoint_utils, method, arguments):
    ing_ip_mock, ing_ip_mock_return_values = url_to_service_endpoint_utils
    create_custom_client_mock, custom_client = custom_client_mock_endpoint_utils
    with pytest.raises(KubernetesUpdateException):
        custom_client.get_namespaced_custom_object.return_value = {'spec': {}}
        custom_client.patch_namespaced_custom_object.side_effect = ApiException()
        method(parameters=arguments, namespace="test", endpoint_name="test",
               id_token=user_token)
        method(parameters=arguments, namespace="test", id_token=user_token)
    create_custom_client_mock.assert_called_once()
    custom_client.get_namespaced_custom_object.assert_called_once()
    custom_client.patch_namespaced_custom_object.assert_called_once()


@pytest.mark.parametrize("method, arguments", call_data)
def test_patch_endpoint_success(custom_client_mock_endpoint_utils,
                                url_to_service_endpoint_utils, method, arguments):
    ing_ip_mock, ing_ip_mock_return_values = url_to_service_endpoint_utils
    create_custom_client_mock, custom_client = custom_client_mock_endpoint_utils
    custom_client.get_namespaced_custom_object.return_value = {'spec': {}}
    method(parameters=arguments, namespace="test", endpoint_name="test",
           id_token=user_token)
    create_custom_client_mock.assert_called_once()
    custom_client.get_namespaced_custom_object.assert_called_once()
    custom_client.patch_namespaced_custom_object.assert_called_once()
    ing_ip_mock.assert_called_once()


@pytest.mark.parametrize("tenant_exception, k8s_exception",
                         [(True, False),
                          (False, True),
                          (False, False)])
def test_list_endpoints(mocker, apps_client_mock_endpoint_utils, tenant_exception, k8s_exception):
    tenant_exists_mock = mocker.patch(
        'management_api.endpoints.endpoint_utils.tenant_exists')
    create_apps_client_mock, apps_client = apps_client_mock_endpoint_utils
    if tenant_exception:
        with pytest.raises(TenantDoesNotExistException):
            tenant_exists_mock.return_value = False
            list_endpoints(namespace="test", id_token=user_token)
    else:
        tenant_exists_mock.return_value = True
        if k8s_exception:
            with pytest.raises(KubernetesGetException):
                apps_client.list_namespaced_deployment.side_effect = ApiException()
                list_endpoints(namespace="test", id_token=user_token)
        else:
            endpoints_name_status_mock = mocker.patch(
                'management_api.endpoints.endpoint_utils.get_endpoints_metadata')
            endpoints_name_status_mock.return_value = {}
            apps_client.list_namespaced_deployment.return_value = {}
            list_endpoints(namespace="test",  id_token=user_token)

            endpoints_name_status_mock.assert_called_once()

        create_apps_client_mock.assert_called_once()
        apps_client.list_namespaced_deployment.assert_called_once()

    tenant_exists_mock.assert_called_once()


def test_create_url_to_service(mocker):
    api_client = Mock()
    create_custom_client_mock = mocker.patch('management_api.endpoints.endpoint_utils.'
                                             'get_k8s_api_client')
    create_custom_client_mock.return_value = api_client
    mock_return_value = ['t_end-t_ns.default', 443]
    external_address_mock = mocker.patch('management_api.utils.kubernetes_resources.'
                                         'get_ingress_external_ip')
    external_address_mock.return_value = mock_return_value
    external_address = "{}:{}".format(mock_return_value[0], mock_return_value[1])
    expected_output = external_address
    output = create_url_to_service(endpoint_name='t_end', namespace="t_ns")
    assert expected_output == output


@pytest.mark.parametrize("tenant_exception, endpoint_exception",
                         [(True, False),
                          (False, True)])
def test_view_endpoint_fail(mocker, tenant_exception, endpoint_exception):
    tenant_exists_mock = mocker.patch(
        'management_api.endpoints.endpoint_utils.tenant_exists')
    endpoint_exists_mock = mocker.patch('management_api.endpoints.endpoint_utils.endpoint_exists')
    if tenant_exception:
        with pytest.raises(TenantDoesNotExistException):
            tenant_exists_mock.return_value = False
            view_endpoint(namespace="test", endpoint_name="test", id_token=user_token)
    elif endpoint_exception:
        with pytest.raises(EndpointDoesNotExistException):
            endpoint_exists_mock.return_value = False
            view_endpoint(namespace="test", endpoint_name="test", id_token=user_token)

            tenant_exists_mock.assert_called_once()
            endpoint_exists_mock.assert_called_once()

    tenant_exists_mock.assert_called_once()


def test_view_endpoint_success(mocker, api_client_mock_endpoint_utils,
                               custom_client_mock_endpoint_utils, apps_client_mock_endpoint_utils):
    tenant_exists_mock = mocker.patch(
        'management_api.endpoints.endpoint_utils.tenant_exists')
    endpoint_exists_mock = mocker.patch('management_api.endpoints.endpoint_utils.endpoint_exists')
    tenant_exists_mock.return_value = True
    endpoint_exists_mock.return_value = True

    create_api_client_mock, api_client = api_client_mock_endpoint_utils
    create_custom_client_mock, custom_client = custom_client_mock_endpoint_utils
    create_apps_client_mock, apps_client = apps_client_mock_endpoint_utils

    endpoint_status_mock = mocker.patch(
        'management_api.endpoints.endpoint_utils.get_endpoint_status', api_instance=api_client)
    endpoint_status_mock.return_value = {}
    model_path_mock = mocker.patch(
        'management_api.endpoints.endpoint_utils.create_url_to_service')
    model_path_mock.return_value = {}
    subject_name_resources_mock = mocker.patch(
        'management_api.endpoints.endpoint_utils.get_crd_subject_name_and_resources',
        custom_api_instance=custom_client)
    subject_name_resources_mock.return_value = "", ""
    replicas_mock = mocker.patch('management_api.endpoints.endpoint_utils.get_replicas',
                                 apps_api_instance=apps_client)
    replicas_mock.return_value = 1
    view_endpoint(namespace="test", endpoint_name="test", id_token=user_token)

    tenant_exists_mock.assert_called_once()
    endpoint_exists_mock.assert_called_once()
    endpoint_status_mock.assert_called_once()
    model_path_mock.assert_called_once()
    subject_name_resources_mock.assert_called_once()
    replicas_mock.assert_called_once()
    create_api_client_mock.assert_called_once()
    create_custom_client_mock.assert_called_once()
    create_apps_client_mock.assert_called_once()
