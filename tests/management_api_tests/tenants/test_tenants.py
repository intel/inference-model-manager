import pytest
import requests
import json

from conftest import MANAGEMENT_API_URL, TENANT_NAME, CERT, SCOPE_NAME, QUOTA, DEFAULT_HEADERS, \
                    WRONG_BODIES, QUOTA_WRONG_VALUES, WRONG_TENANT_NAMES, \
    WRONG_CERTS, PORTABLE_SECRETS_PATHS, api_instance

from tenant_utils import does_secret_exist_in_namespace, \
    is_copied_secret_data_matching_original

def test_create_tenant():
    headers = DEFAULT_HEADERS
    data = json.dumps({
        'name': TENANT_NAME,
        'cert': CERT,
        'scope': SCOPE_NAME,
        'quota': QUOTA,
    })

    url = MANAGEMENT_API_URL

    response = requests.post(url, data=data, headers=headers)
    assert response.text =='Tenant {} created\n'.format(TENANT_NAME) 
    assert response.status_code == 200


@pytest.mark.parametrize("wrong_body, expected_error", WRONG_BODIES)
def test_not_create_tenant_inproper_body(wrong_body, expected_error):
    headers = DEFAULT_HEADERS
    data = json.dumps(wrong_body)

    url = MANAGEMENT_API_URL

    response = requests.post(url, data=data, headers=headers)

    assert response.text == expected_error
    assert response.status_code == 400


@pytest.mark.parametrize("wrong_name, expected_error", WRONG_TENANT_NAMES)
def test_not_create_tenant_wrong_name(wrong_name, expected_error):
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


@pytest.mark.parametrize("quota_wrong_values, expected_error", QUOTA_WRONG_VALUES)
def test_not_create_tenant_wrong_quota(quota_wrong_values, expected_error):
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


@pytest.mark.parametrize("wrong_cert, expected_error", WRONG_CERTS)
def test_not_create_tenant_with_wrong_cert(wrong_cert, expected_error):
    data = json.dumps({
        'cert': wrong_cert,
        'scope': SCOPE_NAME,
        'name': TENANT_NAME,
        'quota': QUOTA,
    })
    url = MANAGEMENT_API_URL
    response = requests.post(url, data=data, headers=DEFAULT_HEADERS)
    assert response.text == expected_error
    assert response.status_code == 400


def test_portable_secrets_propagation_succeeded():
    data = json.dumps({
        'cert': CERT,
        'scope': SCOPE_NAME,
        'name': TENANT_NAME,
        'quota': QUOTA,
    })

    url = MANAGEMENT_API_URL
    response = requests.post(url, data=data, headers=DEFAULT_HEADERS)
    for secret_path in PORTABLE_SECRETS_PATHS:
        secret_namespace, secret_name = secret_path.split('/')
        assert does_secret_exist_in_namespace(api_instance, secret_name,
                                              secret_namespace=TENANT_NAME)
        assert is_copied_secret_data_matching_original(api_instance, secret_name,
                                                       secret_namespace,
                                                       copied_secret_namespace=TENANT_NAME)

