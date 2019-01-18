#
# Copyright (c) 2018-2019 Intel Corporation
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

import boto3
import os
from botocore.client import Config
from kubernetes import client

HOSTNAME = os.getenv('HOSTNAME', 'localhost')
PORT = int(os.getenv('PORT', 5000))
MINIO_ACCESS_KEY_ID = os.getenv('MINIO_ACCESS_KEY_ID', 'default')
MINIO_SECRET_ACCESS_KEY = os.getenv('MINIO_SECRET_ACCESS_KEY', 'default')
MINIO_ENDPOINT_ADDR = os.getenv('MINIO_ENDPOINT_ADDR', 'http://127.0.0.1:9000')

MINIO_REGION = os.getenv('MINIO_REGION', "us-east-1")
SIGNATURE_VERSION = os.getenv('MINIO_SIGNATURE_VERSION', "s3v4")

PLATFORM_DOMAIN = os.getenv('PLATFORM_DOMAIN', 'default')
PLATFORM_ADMIN_LABEL = os.getenv('PLATFORM_ADMIN_LABEL', 'platform_admin')

DEX_URL = os.getenv('DEX_URL', 'https://dex:443')
DEX_EXTERNAL_URL = os.getenv('DEX_EXTERNAL_URL', f'dex.{PLATFORM_DOMAIN}:443')

DEFAULT_MODEL_VERSION_POLICY = '{latest{}}'


# AUTH CONTROLLER DEFINITIONS:
class AuthParameters:
    OOB_REDIRECT_URL = 'urn:ietf:wg:oauth:2.0:oob'  # out of browser
    REDIRECT_URL = os.getenv('AUTH_REDIRECT_URL', 'http://127.0.0.1:5555/callback')
    CLIENT_ID = os.getenv('AUTH_CLIENT_ID', 'example-app')
    RESPONSE_TYPE = 'code'
    SCOPE = 'groups openid email'
    CLIENT_SECRET = os.getenv('AUTH_CLIENT_SECRET', 'ZXhhbXBsZS1hcHAtc2VjcmV0')
    TOKEN_PATH = os.getenv('TOKEN_PATH', '/dex/token')
    AUTH_PATH = os.getenv('AUTH_PATH', '/dex/auth')
    KEYS_PATH = os.getenv('KEYS_PATH', '/dex/keys')
    ADMIN_SCOPE = os.getenv('ADMIN_SCOPE', 'admin')


# CRD DEFINITIONS:
CRD_GROUP = 'ai.intel.com'
CRD_VERSION = 'v1'
CRD_PLURAL = 'inference-endpoints'
CRD_API_VERSION = f'{CRD_GROUP}/{CRD_VERSION}'
CRD_NAMESPACE = os.getenv('CRD_NAMESPACE', 'crd')
CRD_KIND = 'InferenceEndpoint'

ING_NAME = 'ingress-nginx'
ING_NAMESPACE = os.getenv('ING_NAMESPACE', 'ingress-nginx')

MGT_API_NAMESPACE = os.getenv('MGT_API_NAMESPACE', 'man-api')
CERT_SECRET_NAME = 'ca-cert-secret'
PORTABLE_SECRETS_PATHS = [f'{MGT_API_NAMESPACE}/minio-access-info',
                          f'{MGT_API_NAMESPACE}/tls-secret']

minio_client = boto3.client('s3',
                            endpoint_url=MINIO_ENDPOINT_ADDR,
                            aws_access_key_id=MINIO_ACCESS_KEY_ID,
                            aws_secret_access_key=MINIO_SECRET_ACCESS_KEY,
                            config=Config(
                                signature_version=SIGNATURE_VERSION),
                            region_name=MINIO_REGION)

minio_resource = boto3.resource('s3',
                                endpoint_url=MINIO_ENDPOINT_ADDR,
                                aws_access_key_id=MINIO_ACCESS_KEY_ID,
                                aws_secret_access_key=MINIO_SECRET_ACCESS_KEY,
                                config=Config(
                                    signature_version=SIGNATURE_VERSION),
                                region_name=MINIO_REGION)


# To edit this object please first use deep copy
DELETE_BODY = client.V1DeleteOptions()

# -------------------------------------------
K8S_FORBIDDEN = 403
RESOURCE_DOES_NOT_EXIST = 404
NAMESPACE_BEING_DELETED = 409
TERMINATION_IN_PROGRESS = 'Terminating'
NO_SUCH_BUCKET_EXCEPTION = 'NoSuchBucket'


class ValidityMessage:
    CERTIFICATE = "Provided certificate does not look like valid certificate. " \
                  "Please check if it's correctly Base64 encoded and not corrupted " \
                  "in any way."


class EndpointPodStatus:
    UNAVAILABLE_AND_AVAILABLE = (not None, not None)
    ONLY_UNAVAILABLE = (not None, None)
    ONLY_AVAILABLE = (None, not None)
    SCALED_TO_ZERO = (None, None)


STATUSES = {EndpointPodStatus.UNAVAILABLE_AND_AVAILABLE: 'Not fully available',
            EndpointPodStatus.ONLY_UNAVAILABLE: 'Unavailable',
            EndpointPodStatus.ONLY_AVAILABLE: 'Available',
            EndpointPodStatus.SCALED_TO_ZERO: 'Scaled to 0'}
