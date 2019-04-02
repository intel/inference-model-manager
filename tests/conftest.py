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
import boto3
import json
import os
import pytest
import requests
import time
from bs4 import BeautifulSoup
from botocore.client import Config
from kubernetes import config, client
from kubernetes.client.configuration import Configuration
from kubernetes.client.rest import ApiException, RESTClientObject
from urllib.parse import urljoin, urlparse, parse_qs

from config import MINIO_SECRET_ACCESS_KEY, MINIO_ACCESS_KEY_ID, \
    MINIO_REGION, MINIO_ENDPOINT_ADDR, SIGNATURE_VERSION, CRD_VERSION, CRD_PLURAL, CRD_KIND, \
    CRD_GROUP, CRD_API_VERSION, TENANT_NAME, TENANT_RESOURCES, ENDPOINT_RESOURCES, \
    AUTH_MANAGEMENT_API_URL, GENERAL_TENANT_NAME, SENSIBLE_ENDPOINT_RESOURCES, \
    ENDPOINTS_MANAGEMENT_API_URL, DEFAULT_HEADERS
from context import Context
from management_api_tests.reused import transform_quota
from management_api_tests.authenticate import VENUS_CREDENTIALS

from e2e_tests import management_api_requests as api_requests


# Author of this solutions is https://github.com/johnmarcou
# It has been published here: https://github.com/kubernetes-client/python/issues/411
class K8sApiClient(client.ApiClient):
    def call_api(self, *args, async=None, **kwargs):
        return super().call_api(*args, async=False, **kwargs)

    def __init__(self, configuration=None, header_name=None, header_value=None, cookie=None):
        if configuration is None:
            configuration = Configuration()
        self.configuration = configuration

        #        self.pool = ThreadPool()
        self.rest_client = RESTClientObject(configuration)
        self.default_headers = {}
        if header_name is not None:
            self.default_headers[header_name] = header_value
        self.cookie = cookie
        # Set default User-Agent.
        self.user_agent = 'Swagger-Codegen/4.0.0/python'

    def __del__(self):
        pass


@pytest.fixture(scope="session")
def configuration():
    return config.load_kube_config()


@pytest.fixture(scope="session")
def api_instance(configuration):
    return client.CoreV1Api(K8sApiClient(configuration))


@pytest.fixture(scope="session")
def rbac_api_instance(configuration):
    return client.RbacAuthorizationV1Api(K8sApiClient(configuration))


@pytest.fixture(scope="session")
def apps_api_instance(configuration):
    return client.AppsV1Api(K8sApiClient(configuration))


@pytest.fixture(scope="session")
def get_k8s_custom_obj_client(configuration):
    return client.CustomObjectsApi(K8sApiClient(configuration))


@pytest.fixture(scope="function")
def auth_code_for_jane():
    response = requests.get(AUTH_MANAGEMENT_API_URL, allow_redirects=False)
    auth_dex_url = response.headers['location']
    parsed_url = urlparse(auth_dex_url)
    dex_base_url = '{uri.scheme}://{uri.netloc}/'.format(uri=parsed_url)

    resp = requests.get(auth_dex_url)
    soup = BeautifulSoup(resp.text, 'html.parser')
    login_form_action = urljoin(dex_base_url, soup.form['action'])

    data = VENUS_CREDENTIALS
    resp = requests.post(login_form_action, data=data, allow_redirects=False)

    resp = requests.get(urljoin(dex_base_url, resp.headers['Location']), allow_redirects=False)
    query = urlparse(resp.headers['Location']).query
    auth_code = parse_qs(query)['code'][0]

    return auth_code


@pytest.fixture(scope="function")
def function_context(request, get_k8s_custom_obj_client, api_instance, minio_resource,
                     minio_client):
    context = Context(k8s_client=api_instance, k8s_client_custom=get_k8s_custom_obj_client,
                      minio_resource_client=minio_resource, minio_client=minio_client)
    request.addfinalizer(context.delete_all_objects)
    return context


@pytest.fixture(scope="session")
def session_context(request, get_k8s_custom_obj_client, api_instance, minio_resource, minio_client):
    context = Context(k8s_client=api_instance, k8s_client_custom=get_k8s_custom_obj_client,
                      minio_resource_client=minio_resource, minio_client=minio_client)
    request.addfinalizer(context.delete_all_objects)
    return context


@pytest.fixture(scope="session")
def minio_client():
    return boto3.client('s3',
                        endpoint_url=MINIO_ENDPOINT_ADDR,
                        aws_access_key_id=MINIO_ACCESS_KEY_ID,
                        aws_secret_access_key=MINIO_SECRET_ACCESS_KEY,
                        config=Config(
                            signature_version=SIGNATURE_VERSION),
                        region_name=MINIO_REGION)


@pytest.fixture(scope="session")
def minio_resource():
    return boto3.resource('s3',
                          endpoint_url=MINIO_ENDPOINT_ADDR,
                          aws_access_key_id=MINIO_ACCESS_KEY_ID,
                          aws_secret_access_key=MINIO_SECRET_ACCESS_KEY,
                          config=Config(
                              signature_version=SIGNATURE_VERSION),
                          region_name=MINIO_REGION)


def get_model_from_google_storage(model_name):
    model_url_base = "https://storage.googleapis.com/inference-eu/models_zoo/" \
                     + model_name + "/frozen_" + model_name

    print("Downloading " + model_name + " model...")
    response = requests.get(model_url_base + '.bin', stream=True)
    with open(model_name + '.bin', 'wb') as output:
        output.write(response.content)
    response = requests.get(model_url_base + '.xml', stream=True)
    with open(model_name + '.xml', 'wb') as output:
        output.write(response.content)
    return model_name + '.bin', model_name + '.xml'


def upload_model_to_minio(minio_resource, tenant, model_name):
    path_to_bin_file, path_to_xml_file = get_model_from_google_storage("resnet_V1_50")
    bin_key = f"{model_name}/1/{path_to_bin_file}"
    xml_key = f"{model_name}/1/{path_to_xml_file}"
    minio_resource.meta.client.upload_file(path_to_bin_file, tenant, bin_key)
    minio_resource.meta.client.upload_file(path_to_xml_file, tenant, xml_key)
    os.remove(path_to_bin_file)
    os.remove(path_to_xml_file)


def create_tenant(name, quota, context):
    response = api_requests.create_tenant(name=name, resources=quota)
    context.add_object(object_type='tenant', object_to_delete={'name': name})
    time.sleep(20)
    assert response.status_code == 200
    return name, quota


def create_endpoint(custom_obj_client, namespace, context, endpoint_name='predict',
                    resources=ENDPOINT_RESOURCES):
    endpoint_resources = transform_quota(resources)
    metadata = {"name": endpoint_name}
    model_name, model_version_policy = 'resnet', '{specific {versions: 1}}'
    model_path = f'{model_name}'
    spec = {
        'modelName': model_name,
        'modelVersionPolicy': model_version_policy,
        'endpointName': endpoint_name,
        'subjectName': 'client',
        'replicas': 1,
        'resources': endpoint_resources,
        'servingName': 'tf-serving',
    }
    body = {"spec": spec, 'kind': CRD_KIND, "replicas": 1,
            "apiVersion": CRD_API_VERSION, "metadata": metadata}
    custom_obj_client. \
        create_namespaced_custom_object(CRD_GROUP, CRD_VERSION, namespace, CRD_PLURAL, body)

    endpoint_to_delete = {'name': endpoint_name, 'namespace': namespace}
    model_to_delete = {'name': model_path, 'namespace': namespace}
    context.add_object(object_type='CRD', object_to_delete=endpoint_to_delete)
    context.add_object(object_type='model', object_to_delete=model_to_delete)

    return body


@pytest.fixture(scope="session")
def session_tenant(api_instance, minio_client, session_context):
    name = GENERAL_TENANT_NAME
    quota = TENANT_RESOURCES
    return create_tenant(name, quota, session_context)


@pytest.fixture(scope="function")
def tenant_with_fake_model(api_instance, minio_client, function_context):
    name = 'fake-model'
    quota = TENANT_RESOURCES
    namespace, quota = create_tenant(name, quota, function_context)
    create_fake_model((namespace, {'spec': {'modelName': 'resnet'}}), minio_client)
    return namespace, quota


@pytest.fixture(scope="function")
def ovms_tenant(api_instance, minio_client, function_context, minio_resource):
    name = "ovms"
    quota = TENANT_RESOURCES
    model_name = "ovms_resnet"
    name, qouta = create_tenant(name, quota, function_context)
    upload_model_to_minio(minio_resource, name, model_name)
    return name, ""


@pytest.fixture(scope="function")
def ovms_endpoint(function_context, ovms_tenant):
    crd_server_name = 'ovms'
    namespace, _ = ovms_tenant
    replicas = 1
    data = json.dumps({
        'modelName': 'ovms_resnet',
        'modelVersion': 1,
        'endpointName': crd_server_name,
        'subjectName': 'client',
        'replicas': replicas,
        'resources': SENSIBLE_ENDPOINT_RESOURCES,
        'servingName': 'ovms'
    })
    url = ENDPOINTS_MANAGEMENT_API_URL.format(tenant_name=namespace)

    response = requests.post(url, data=data, headers=DEFAULT_HEADERS, verify=False)

    assert response.status_code == 200
    assert "created" in response.text

    function_context.add_object(object_type='CRD', object_to_delete={'name': crd_server_name,
                                                                     'namespace': namespace})
    return response, namespace


@pytest.fixture(scope="function")
def tenant_with_endpoint_parametrized_max_endpoints(
        request, api_instance, minio_client, function_context, get_k8s_custom_obj_client):
    name = TENANT_NAME
    tenant_quota = TENANT_RESOURCES
    tenant_quota["maxEndpoints"] = request.param
    create_tenant(name, tenant_quota, function_context)
    body = create_endpoint(get_k8s_custom_obj_client, name, function_context)
    return name, body


@pytest.fixture(scope="function")
def tenant_with_endpoint(function_context, session_tenant, get_k8s_custom_obj_client):
    namespace, _ = session_tenant
    body = create_endpoint(get_k8s_custom_obj_client, namespace, function_context)
    return namespace, body


@pytest.fixture(scope="session")
def fake_saturn_tenant():
    name = "saturn-tenant"
    quota = {}
    return name, quota


@pytest.fixture(scope="function")
def empty_tenant(session_tenant):
    return create_dummy_tenant(session_tenant)


@pytest.fixture(scope="function")
def fake_tenant_endpoint(fake_saturn_tenant):
    return create_dummy_tenant(fake_saturn_tenant)


def create_dummy_tenant(session_tenant):
    name, _ = session_tenant
    body = {}
    return name, body


@pytest.fixture(scope="function")
def fake_endpoint(session_tenant):
    namespace, _ = session_tenant
    model_name, model_version_policy = 'fake', '{specific {versions: 1}}'
    body = {'spec': {'modelName': model_name,
                     'modelVersionPolicy': model_version_policy}}
    return namespace, body


def create_fake_model(endpoint, minio_client):
    namespace, body = endpoint
    model_name = body['spec']['modelName']
    model_path = f'{model_name}/1/model.pb'
    minio_client.put_object(Bucket=namespace, Body=b'Some model content', Key=model_path)
    return namespace, body


@pytest.fixture(scope="function")
def endpoint_with_fake_model(tenant_with_endpoint, minio_client):
    return create_fake_model(tenant_with_endpoint, minio_client)


@pytest.fixture(scope="function")
def fake_endpoint_with_fake_model(fake_endpoint, minio_client):
    return create_fake_model(fake_endpoint, minio_client)


def download_saved_model_from_path(path, file_name='saved_model.pb'):
    response = requests.get(path)
    with open(file_name, 'wb') as f:
        f.write(response.content)


def list_namespaces():
    try:
        k8s_client = client.CoreV1Api(client.ApiClient(config.load_kube_config()))
        api_response = k8s_client.list_namespace()
    except ApiException as e:
        api_response = e
        print("Exception when calling CoreV1Api->list_namespace: %s\n" % e)

    return api_response


def get_all_pods_in_namespace(namespace, label_selector=''):
    try:
        k8s_client = client.CoreV1Api(client.ApiClient(config.load_kube_config()))
        api_response = k8s_client.list_namespaced_pod(namespace=namespace,
                                                      label_selector=label_selector)
    except ApiException as e:
        api_response = e
        print("Exception when calling CoreV1Api->list_pod_for_all_namespaces: %s\n" % e)

    return api_response


def get_logs_of_pod(namespace, pod):
    api_instance = client.CoreV1Api(client.ApiClient(config.load_kube_config()))
    return api_instance.read_namespaced_pod_log(pod, namespace)


def resource_quota(api_instance, quota={}, namespace=TENANT_NAME):
    name_object = client.V1ObjectMeta(name=namespace)
    resource_quota_spec = client.V1ResourceQuotaSpec(hard=quota)
    body = client.V1ResourceQuota(spec=resource_quota_spec, metadata=name_object)
    api_instance.create_namespaced_resource_quota(namespace=namespace, body=body)
    return quota


def get_endpoint_ingress(name, namespace):
    extensions_api_instance = client.ExtensionsV1beta1Api(config.load_kube_config())
    api_response = extensions_api_instance.read_namespaced_ingress(name, namespace)
    return api_response


def get_ingress_subject_name(name, namespace):
    metadata = get_endpoint_ingress(name, namespace).metadata
    subject_name = metadata.annotations['allowed-values']
    return subject_name


def get_url_from_response(endpoint_response):
    url = json.loads(endpoint_response.text)['data']['url']
    return url
