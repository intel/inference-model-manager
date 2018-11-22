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

import pytest
import requests
import json

from management_api_tests.config import TENANT_NAME, ADMIN_HEADERS, CERT, SCOPE_NAME, \
    QUOTA, QUOTA_WRONG_VALUES, QUOTA_REGEX, TENANTS_MANAGEMENT_API_URL, PORTABLE_SECRETS_PATHS, \
    WRONG_CERTS, WRONG_BODIES, CheckResult
from management_api_tests.tenants.tenant_utils import check_namespaced_secret_existence, \
    check_copied_secret_data_matching_original, check_bucket_existence, \
    check_namespace_availability, check_resource_quota_matching_provided, check_role_existence, \
    check_rolebinding_existence


def test_create_tenant(function_context, minio_client, api_instance, rbac_api_instance):
    data = json.dumps({
        'name': TENANT_NAME,
        'cert': CERT,
        'scope': SCOPE_NAME,
        'quota': QUOTA,
    })

    url = TENANTS_MANAGEMENT_API_URL

    response = requests.post(url, data=data, headers=ADMIN_HEADERS)
    function_context.add_object(object_type='tenant', object_to_delete={'name': TENANT_NAME})

    assert response.text == 'Tenant {} created\n'.format(TENANT_NAME)
    assert response.status_code == 200
    assert check_namespace_availability(api_instance,
                                        namespace=TENANT_NAME) == CheckResult.RESOURCE_AVAILABLE
    assert check_bucket_existence(minio_client,
                                  bucket=TENANT_NAME) == CheckResult.RESOURCE_AVAILABLE

    assert check_role_existence(rbac_api_instance, namespace=TENANT_NAME,
                                role=TENANT_NAME) == CheckResult.RESOURCE_AVAILABLE
    assert check_rolebinding_existence(rbac_api_instance, namespace=TENANT_NAME,
                                       rolebinding=TENANT_NAME) == CheckResult.RESOURCE_AVAILABLE


def test_not_create_tenant_already_exists(session_tenant, minio_client, api_instance):
    name, _ = session_tenant
    data = {
        'name': name,
        'cert': CERT,
        'scope': SCOPE_NAME,
        'quota': QUOTA,
    }
    url = TENANTS_MANAGEMENT_API_URL

    data['quota']['limits.cpu'] = '3'
    response = requests.post(url, data=json.dumps(data), headers=ADMIN_HEADERS)
    data['quota'].pop('maxEndpoints')

    assert response.status_code == 409
    assert check_namespace_availability(api_instance,
                                        namespace=name) == CheckResult.RESOURCE_AVAILABLE
    assert check_bucket_existence(minio_client,
                                  bucket=name) == CheckResult.RESOURCE_AVAILABLE
    assert check_resource_quota_matching_provided(
        api_instance, name, provided_quota=data['quota']) == CheckResult.CONTENTS_MISMATCHING


@pytest.mark.parametrize("wrong_body, expected_error, expected_message", WRONG_BODIES)
def test_not_create_tenant_improper_body(wrong_body, expected_error, expected_message,
                                         minio_client, api_instance):
    data = json.dumps(wrong_body)
    url = TENANTS_MANAGEMENT_API_URL
    response = requests.post(url, data=data, headers=ADMIN_HEADERS)

    assert expected_message in response.text
    assert expected_error == response.status_code
    if 'name' in wrong_body and wrong_body['name']:
        assert check_bucket_existence(minio_client, bucket=wrong_body['name']) == \
               CheckResult.RESOURCE_DOES_NOT_EXIST
        assert check_namespace_availability(
            api_instance, namespace=wrong_body['name']) == CheckResult.RESOURCE_DOES_NOT_EXIST


@pytest.mark.parametrize("wrong_cert, expected_error", WRONG_CERTS)
def test_not_create_tenant_with_wrong_cert(wrong_cert, expected_error, minio_client, api_instance):
    data = json.dumps({
        'cert': wrong_cert,
        'scope': SCOPE_NAME,
        'name': TENANT_NAME,
        'quota': QUOTA,
    })
    url = TENANTS_MANAGEMENT_API_URL
    response = requests.post(url, data=data, headers=ADMIN_HEADERS)
    assert expected_error in response.text
    assert response.status_code == 400
    assert check_bucket_existence(minio_client,
                                  bucket=TENANT_NAME) == CheckResult.RESOURCE_DOES_NOT_EXIST
    assert check_namespace_availability(api_instance,
                                        namespace=TENANT_NAME
                                        ) == CheckResult.RESOURCE_DOES_NOT_EXIST


@pytest.mark.parametrize("quota_wrong_values, expected_error", QUOTA_WRONG_VALUES)
def test_not_create_tenant_wrong_quota(quota_wrong_values,
                                       expected_error, minio_client, api_instance):
    data = json.dumps({
        'name': TENANT_NAME,
        'cert': CERT,
        'scope': SCOPE_NAME,
        'quota': quota_wrong_values,
    })
    url = TENANTS_MANAGEMENT_API_URL
    response = requests.post(url, data=data, headers=ADMIN_HEADERS)

    assert expected_error.format(QUOTA_REGEX) in response.text
    assert response.status_code == 400
    assert check_bucket_existence(minio_client,
                                  bucket=TENANT_NAME) == CheckResult.RESOURCE_DOES_NOT_EXIST
    assert check_namespace_availability(api_instance, namespace=TENANT_NAME) == CheckResult. \
        RESOURCE_DOES_NOT_EXIST


def test_portable_secrets_propagation_succeeded(function_context, minio_client, api_instance):
    data = json.dumps({
        'cert': CERT,
        'scope': SCOPE_NAME,
        'name': TENANT_NAME,
        'quota': QUOTA,
    })

    url = TENANTS_MANAGEMENT_API_URL
    requests.post(url, data=data, headers=ADMIN_HEADERS)
    function_context.add_object(object_type='tenant', object_to_delete={'name': TENANT_NAME})

    assert check_bucket_existence(minio_client,
                                  bucket=TENANT_NAME) == CheckResult.RESOURCE_AVAILABLE
    assert check_namespace_availability(api_instance,
                                        namespace=TENANT_NAME) == CheckResult.RESOURCE_AVAILABLE

    for secret_path in PORTABLE_SECRETS_PATHS:
        secret_namespace, secret_name = secret_path.split('/')

        assert check_namespaced_secret_existence(
            api_instance, secret_name, secret_namespace=TENANT_NAME
        ) == CheckResult.RESOURCE_AVAILABLE

        assert check_copied_secret_data_matching_original(
            api_instance, secret_name, secret_namespace, copied_secret_namespace=TENANT_NAME
        ) == CheckResult.CONTENTS_MATCHING


def test_delete_tenant(minio_client, api_instance):
    url = TENANTS_MANAGEMENT_API_URL
    new_tenant_name = TENANT_NAME + '-delete'
    data = json.dumps({
        'cert': CERT,
        'scope': SCOPE_NAME,
        'name': new_tenant_name,
        'quota': QUOTA,
    })
    requests.post(url, data=data, headers=ADMIN_HEADERS)
    data = json.dumps({
        'name': new_tenant_name,
    })
    response = requests.delete(url, data=data, headers=ADMIN_HEADERS)
    assert response.text == 'Tenant {} deleted\n'.format(new_tenant_name)
    assert response.status_code == 200

    assert check_bucket_existence(
        minio_client, bucket=new_tenant_name) == CheckResult.RESOURCE_DOES_NOT_EXIST

    namespace_status = check_namespace_availability(api_instance, namespace=new_tenant_name)
    assert namespace_status == CheckResult.\
        RESOURCE_DOES_NOT_EXIST or namespace_status == CheckResult.RESOURCE_BEING_DELETED


def test_list_tenants(session_tenant):
    namespace, _ = session_tenant
    url = TENANTS_MANAGEMENT_API_URL
    response = requests.get(url, headers=ADMIN_HEADERS)
    assert f"Tenants present on platform: ['{namespace}']" in response.text
    assert response.status_code == 200
