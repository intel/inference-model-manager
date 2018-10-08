import requests
import json

from management_api_tests.config import DEFAULT_HEADERS, ADMIN_HEADERS, SCOPE_NAME, \
    TENANT_RESOURCES, TENANTS_MANAGEMENT_API_URL, ENDPOINT_MANAGEMENT_API_URL
from e2e_tests.config import TENANT_NAME, MODEL_NAME, CERT


def create_tenant():
    headers = ADMIN_HEADERS
    data = json.dumps({
        'name': TENANT_NAME,
        'cert': CERT,
        'scope': SCOPE_NAME,
        'quota': TENANT_RESOURCES,
    })
    url = TENANTS_MANAGEMENT_API_URL

    response = requests.post(url, data=data, headers=headers)
    return response


def create_endpoint():
    headers = DEFAULT_HEADERS
    data = json.dumps({
        'modelName': MODEL_NAME,
        'modelVersion': 1,
        'endpointName': MODEL_NAME+'endpoint',
        'subjectName': 'client',
        'resources': TENANT_RESOURCES,
    })
    url = ENDPOINT_MANAGEMENT_API_URL

    response = requests.post(url, data=data, headers=headers)
    return response
