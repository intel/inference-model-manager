#
# Copyright (c) 2019 Intel Corporation
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

import os
import urllib.parse
from management_api_tests.authenticate import get_user_token, get_admin_token, \
    get_token

MINIO_ACCESS_KEY_ID = os.environ.get('MINIO_ACCESS_KEY',
                                     'AKIAIOSFODNN7EXAMPLE')
MINIO_SECRET_ACCESS_KEY = os.environ.get('MINIO_SECRET_KEY',
                                         'wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY')
MINIO_ENDPOINT_ADDR = os.environ.get('MINIO_ENDPOINT_ADDR', 'http://127.0.0.1:9000')
MINIO_REGION = os.environ.get('MINIO_REGION', 'us-east-1')
SIGNATURE_VERSION = 's3v4'

CRD_GROUP = 'ai.intel.com'
CRD_VERSION = 'v1'
CRD_PLURAL = 'inference-endpoints'
CRD_API_VERSION = f'{CRD_GROUP}/{CRD_VERSION}'
CRD_KIND = 'InferenceEndpoint'

TENANT_NAME = os.environ.get('TENANT_NAME', 'function-tenant')
GENERAL_TENANT_NAME = os.environ.get('GENERAL_TENANT_NAME', 'test-tenant')

# scope name should be 'test' because tests are performed in tenant 'test'
# so rolebinding, scope in token and namespace name matches together
SCOPE_NAME = os.environ.get('SCOPE_NAME', 'test')


TENANT_RESOURCES = {'limits.cpu': '4', 'limits.memory': '4Gi', 'requests.cpu': '1',
                    'requests.memory': '1Gi'}

SENSIBLE_ENDPOINT_RESOURCES = {'limits.cpu': '1000m', 'limits.memory': '1000Mi',
                               'requests.cpu': '100m', 'requests.memory': '100Mi'}


ENDPOINT_RESOURCES = {'limits.cpu': '200m', 'limits.memory': '200Mi', 'requests.cpu': '0m',
                      'requests.memory': '0Mi'}


MANAGEMENT_API_URL = os.environ.get('MANAGEMENT_API_URL', 'http://127.0.0.1:5000')
TENANTS_MANAGEMENT_API_URL = urllib.parse.urljoin(MANAGEMENT_API_URL, 'tenants')
ENDPOINTS_MANAGEMENT_API_URL = urllib.parse.urljoin(MANAGEMENT_API_URL, 'tenants/' +
                                                    '{tenant_name}/endpoints')
ENDPOINT_MANAGEMENT_API_URL_SCALE = ENDPOINTS_MANAGEMENT_API_URL + "/{endpoint_name}/replicas"
ENDPOINT_MANAGEMENT_API_URL = ENDPOINTS_MANAGEMENT_API_URL + "/{endpoint_name}"
START_MULTIPART_UPLOAD_API_URL = urllib.parse.urljoin(MANAGEMENT_API_URL, 'tenants/' +
                                                      '{tenant_name}/' +
                                                      'upload/start')
AUTH_MANAGEMENT_API_URL = urllib.parse.urljoin(MANAGEMENT_API_URL, 'authenticate')
TOKEN_MANAGEMENT_API_URL = urllib.parse.urljoin(MANAGEMENT_API_URL, 'authenticate/token')
MODEL_MANAGEMENT_API_URL = urllib.parse.urljoin(MANAGEMENT_API_URL, 'tenants/{tenant_name}/models')
SERVINGS_MANAGEMENT_API_URL = urllib.parse.urljoin(MANAGEMENT_API_URL, 'servings')
SERVING_MANAGEMENT_API_URL = urllib.parse.urljoin(MANAGEMENT_API_URL, 'servings/{serving_name}')


DEFAULT_HEADERS = {
    'accept': 'application/json',
    'Authorization': get_user_token()['id_token'],
    'Content-Type': 'application/json',
}

ADMIN_HEADERS = {
    'accept': 'application/json',
    'Authorization': get_admin_token()['id_token'],
    'Content-Type': 'application/json',
}

USER1_HEADERS = {
    'accept': 'application/json',
    'Authorization': get_token("mars")['id_token'],
    'Content-Type': 'application/json',
}

USER2_HEADERS = {
    'accept': 'application/json',
    'Authorization': get_token("saturn")['id_token'],
    'Content-Type': 'application/json',
}

CERT = os.environ.get('CERT', 'WRONG_CERT')

CERT_BAD_CLIENT = "../helm-deployment/management-api-subchart/certs/bad-client.crt"
CERT_BAD_CLIENT_KEY = "../helm-deployment/management-api-subchart/certs/bad-client.key"
CERT_CLIENT = "../helm-deployment/management-api-subchart/certs/client-tf.crt"
CERT_CLIENT_KEY = "../helm-deployment/management-api-subchart/certs/client-tf.key"
CERT_SERVER = "../helm-deployment/management-api-subchart/certs/server-tf.crt"
CERT_SERVER_KEY = "../helm-deployment/management-api-subchart/certs/server-tf.key"
