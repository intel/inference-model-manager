import boto3
import pytest
import requests
from tenacity import retry, stop_after_attempt, wait_fixed
from bs4 import BeautifulSoup
from botocore.client import Config
from kubernetes import config, client
from kubernetes.client.rest import ApiException
from urllib.parse import urljoin, urlparse, parse_qs

from management_api_tests.config import MINIO_SECRET_ACCESS_KEY, MINIO_ACCESS_KEY_ID, \
    MINIO_REGION, MINIO_ENDPOINT_ADDR, SIGNATURE_VERSION, CRD_VERSION, CRD_PLURAL, CRD_KIND, \
    CRD_GROUP, CRD_API_VERSION, TENANT_NAME, TENANT_RESOURCES, ENDPOINT_RESOURCES, \
    AUTH_MANAGEMENT_API_URL, JANE
from management_api_tests.context import Context
from management_api_tests.reused import propagate_portable_secrets, transform_quota


@pytest.fixture(scope="session")
def configuration():
    return config.load_kube_config()


@pytest.fixture(scope="session")
def api_instance(configuration):
    return client.CoreV1Api(client.ApiClient(configuration))


@pytest.fixture(scope="session")
def rbac_api_instance(configuration):
    return client.RbacAuthorizationV1Api(client.ApiClient(configuration))


@pytest.fixture(scope="session")
def apps_api_instance(configuration):
    return client.AppsV1Api(client.ApiClient(configuration))


@pytest.fixture(scope="session")
def get_k8s_custom_obj_client(configuration):
    return client.CustomObjectsApi(client.ApiClient(configuration))


@pytest.fixture(scope="function")
def auth_code_for_jane():
    response = requests.get(AUTH_MANAGEMENT_API_URL, allow_redirects=False)
    auth_dex_url = response.headers['location']
    parsed_url = urlparse(auth_dex_url)
    dex_base_url = '{uri.scheme}://{uri.netloc}/'.format(uri=parsed_url)

    resp = requests.get(auth_dex_url, verify=False)
    soup = BeautifulSoup(resp.text, 'html.parser')
    login_form_action = urljoin(dex_base_url, soup.form['action'])

    data = JANE
    resp = requests.post(login_form_action, data=data, allow_redirects=False, verify=False)

    resp = requests.get(urljoin(dex_base_url, resp.headers['Location']), allow_redirects=False,
                        verify=False)
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


@pytest.fixture(scope="function")
def tenant_with_endpoint(function_context, tenant, get_k8s_custom_obj_client):
    namespace, _ = tenant
    metadata = {"name": "predict"}
    resources = transform_quota(ENDPOINT_RESOURCES)
    model_name, model_version = 'resnet', 1
    spec = {
        'modelName': model_name,
        'modelVersion': model_version,
        'endpointName': 'predict',
        'subjectName': 'client',
        'replicas': 1,
        'resources': resources
    }
    body = {"spec": spec, 'kind': CRD_KIND, "replicas": 1,
            "apiVersion": CRD_API_VERSION, "metadata": metadata}
    get_k8s_custom_obj_client. \
        create_namespaced_custom_object(CRD_GROUP, CRD_VERSION, namespace, CRD_PLURAL, body)
    object_to_delete = {'name': "predict", 'namespace': namespace}
    function_context.add_object(object_type='CRD', object_to_delete=object_to_delete)
    return namespace, body


@retry(stop=stop_after_attempt(3), wait=wait_fixed(0.2))
def get_all_pods_in_namespace(k8s_client, namespace, label_selector=''):
    try:
        api_response = k8s_client.list_namespaced_pod(namespace=namespace,
                                                      label_selector=label_selector)
    except ApiException as e:
        print("Exception when calling CoreV1Api->list_pod_for_all_namespaces: %s\n" % e)

    return api_response


def resource_quota(api_instance, quota={}, namespace=TENANT_NAME):
    name_object = client.V1ObjectMeta(name=namespace)
    resource_quota_spec = client.V1ResourceQuotaSpec(hard=quota)
    body = client.V1ResourceQuota(spec=resource_quota_spec, metadata=name_object)
    api_instance.create_namespaced_resource_quota(namespace=namespace, body=body)
    return quota


@pytest.fixture(scope="function")
def tenant(api_instance, minio_client, function_context):
    name = TENANT_NAME
    name_object = client.V1ObjectMeta(name=name)
    namespace = client.V1Namespace(metadata=name_object)
    api_instance.create_namespace(namespace)
    propagate_portable_secrets(api_instance, name)
    quota = resource_quota(api_instance, quota=TENANT_RESOURCES)
    minio_client.create_bucket(Bucket=name)
    function_context.add_object(object_type='tenant', object_to_delete={'name': name})
    return name, quota


@pytest.fixture(scope="session")
def fake_tenant():
    name = "andrzej"  # USER1_HEADERS contain token for andrzej user with scope andrzej
    quota = {}
    return name, quota


@pytest.fixture(scope="function")
def empty_tenant(tenant):
    return create_dummy_tenant(tenant)


@pytest.fixture(scope="function")
def fake_tenant_endpoint(fake_tenant):
    return create_dummy_tenant(fake_tenant)


def create_dummy_tenant(tenant):
    name, _ = tenant
    body = {}
    return name, body


@pytest.fixture(scope="function")
def fake_endpoint(tenant):
    namespace, _ = tenant
    model_name, model_version = 'fake', 1
    body = {'spec': {'modelName': model_name,
                     'modelVersion': model_version}}
    return namespace, body


def create_fake_model(endpoint, minio_client):
    namespace, body = endpoint
    model_name, model_version = body['spec']['modelName'], body['spec']['modelVersion']
    model_path = f'{model_name}-{model_version}/0/model.pb'
    minio_client.put_object(Bucket=namespace, Body=b'Some model content', Key=model_path)
    return namespace, body


@pytest.fixture(scope="function")
def endpoint_with_fake_model(tenant_with_endpoint, minio_client):
    return create_fake_model(tenant_with_endpoint, minio_client)


@pytest.fixture(scope="function")
def fake_endpoint_with_fake_model(fake_endpoint, minio_client):
    return create_fake_model(fake_endpoint, minio_client)
