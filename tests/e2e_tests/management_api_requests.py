import requests
import json

from management_api_tests.config import DEFAULT_HEADERS, ADMIN_HEADERS, SCOPE_NAME, \
    TENANT_RESOURCES, SENSIBLE_ENDPOINT_RESOURCES, TENANTS_MANAGEMENT_API_URL, \
    ENDPOINTS_MANAGEMENT_API_URL
from e2e_tests.config import TENANT_NAME, MODEL_NAME, CERT


def create_tenant(name=TENANT_NAME, headers=ADMIN_HEADERS,
                  scope=SCOPE_NAME, resources=TENANT_RESOURCES, cert=CERT):
    data = json.dumps({
        'name': name,
        'cert': cert,
        'scope': scope,
        'quota': resources,
    })
    url = TENANTS_MANAGEMENT_API_URL

    response = requests.post(url, data=data, headers=headers, verify=False)
    return response


def delete_tenant(headers=ADMIN_HEADERS, name=TENANT_NAME):
    url = TENANTS_MANAGEMENT_API_URL
    data = json.dumps({
        'name': name,
    })
    response = requests.delete(url, data=data, headers=headers, verify=False)
    return response


def create_endpoint(headers=DEFAULT_HEADERS, name=MODEL_NAME,
                    resources=SENSIBLE_ENDPOINT_RESOURCES,
                    tenant=TENANT_NAME):
    data = json.dumps({
        'modelName': name,
        'modelVersion': 1,
        'endpointName': name + 'endpoint',
        'subjectName': 'client',
        'resources': resources,
    })
    url = ENDPOINTS_MANAGEMENT_API_URL.format(tenant_name=tenant)

    response = requests.post(url, data=data, headers=headers, verify=False)
    return response
