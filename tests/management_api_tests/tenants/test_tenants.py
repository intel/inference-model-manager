import pytest
import requests
import json

from conftest import delete_namespace_bucket
from management_api_tests.config import TENANT_NAME, DEFAULT_HEADERS, CERT, SCOPE_NAME, QUOTA, \
    MANAGEMENT_API_URL, WRONG_BODIES, PORTABLE_SECRETS_PATHS, WRONG_TENANT_NAMES, \
    QUOTA_WRONG_VALUES, WRONG_CERTS
from management_api_tests.tenants.tenant_utils import does_secret_exist_in_namespace, \
    is_copied_secret_data_matching_original, is_bucket_available, is_namespace_available


def test_create_tenant(minio_client, api_instance):
    headers = DEFAULT_HEADERS
    data = json.dumps({
        'name': TENANT_NAME,
        'cert': CERT,
        'scope': SCOPE_NAME,
        'quota': QUOTA,
    })

    url = MANAGEMENT_API_URL

    response = requests.post(url, data=data, headers=headers)

    assert response.text == 'Tenant {} created\n'.format(TENANT_NAME)
    assert response.status_code == 200
    assert is_namespace_available(api_instance, namespace=TENANT_NAME)
    assert is_bucket_available(minio_client, bucket=TENANT_NAME)
    delete_namespace_bucket(TENANT_NAME)


@pytest.mark.parametrize("wrong_body, expected_error", WRONG_BODIES)
def test_not_create_tenant_improper_body(wrong_body, expected_error, minio_client, api_instance):
    headers = DEFAULT_HEADERS
    data = json.dumps(wrong_body)

    url = MANAGEMENT_API_URL

    response = requests.post(url, data=data, headers=headers)

    assert response.text == expected_error
    assert response.status_code == 400
    if 'name' in wrong_body and wrong_body['name']:
        assert not is_bucket_available(minio_client, bucket=wrong_body['name'])
        assert not is_namespace_available(api_instance, namespace=wrong_body['name'])


@pytest.mark.parametrize("wrong_name, expected_error", WRONG_TENANT_NAMES)
def test_not_create_tenant_wrong_name(wrong_name, expected_error, minio_client, api_instance):
    headers = DEFAULT_HEADERS
    data = json.dumps({
        'name': wrong_name,
        'cert': CERT,
        'scope': SCOPE_NAME,
        'quota': QUOTA,
    })
    
    url = MANAGEMENT_API_URL

    response = requests.post(url, data=data, headers=headers)

    assert response.text == expected_error
    assert response.status_code == 400
    assert not is_bucket_available(minio_client, bucket=wrong_name)
    assert not is_namespace_available(api_instance, namespace=wrong_name)


@pytest.mark.parametrize("quota_wrong_values, expected_error", QUOTA_WRONG_VALUES)
def test_not_create_tenant_wrong_quota(quota_wrong_values,
                                       expected_error, minio_client, api_instance):
    headers = DEFAULT_HEADERS
    data = json.dumps({
        'name': TENANT_NAME,
        'cert': CERT,
        'scope': SCOPE_NAME,
        'quota': quota_wrong_values,
    })

    url = MANAGEMENT_API_URL

    response = requests.post(url, data=data, headers=headers)

    assert response.text == expected_error
    assert response.status_code == 400
    assert not is_bucket_available(minio_client, bucket=TENANT_NAME)
    assert not is_namespace_available(api_instance, namespace=TENANT_NAME)


@pytest.mark.parametrize("wrong_cert, expected_error", WRONG_CERTS)
def test_not_create_tenant_with_wrong_cert(wrong_cert, expected_error, minio_client, api_instance):
    data = json.dumps({
        'cert': wrong_cert,
        'scope': SCOPE_NAME,
        'name': TENANT_NAME,
        'quota': QUOTA,
    })
    url = MANAGEMENT_API_URL
    response = requests.post(url, data=data, headers=DEFAULT_HEADERS)
    assert expected_error in response.text
    assert response.status_code == 400
    assert not is_bucket_available(minio_client, bucket=TENANT_NAME)
    assert not is_namespace_available(api_instance, namespace=TENANT_NAME)


def test_portable_secrets_propagation_succeeded(minio_client, api_instance):
    data = json.dumps({
        'cert': CERT,
        'scope': SCOPE_NAME,
        'name': TENANT_NAME,
        'quota': QUOTA,
    })

    url = MANAGEMENT_API_URL
    requests.post(url, data=data, headers=DEFAULT_HEADERS)

    assert is_bucket_available(minio_client, bucket=TENANT_NAME)
    assert is_namespace_available(api_instance, namespace=TENANT_NAME)
    for secret_path in PORTABLE_SECRETS_PATHS:
        secret_namespace, secret_name = secret_path.split('/')
        assert does_secret_exist_in_namespace(api_instance, secret_name,
                                              secret_namespace=TENANT_NAME)
        assert is_copied_secret_data_matching_original(api_instance, secret_name,
                                                       secret_namespace,
                                                       copied_secret_namespace=TENANT_NAME)
    delete_namespace_bucket(TENANT_NAME)


def test_delete_tenant(minio_client, api_instance):
    url = MANAGEMENT_API_URL

    data = json.dumps({
        'cert': CERT,
        'scope': SCOPE_NAME,
        'name': TENANT_NAME,
        'quota': QUOTA,
    })

    requests.post(url, data=data, headers=DEFAULT_HEADERS)
    data = json.dumps({
        'name': TENANT_NAME,
    })
    response = requests.delete(url, data=data, headers=DEFAULT_HEADERS)
    assert response.text == 'Tenant {} deleted\n'.format(TENANT_NAME)
    assert response.status_code == 200
    assert not is_bucket_available(minio_client, bucket=TENANT_NAME)
    assert not is_namespace_available(api_instance, namespace=TENANT_NAME)
