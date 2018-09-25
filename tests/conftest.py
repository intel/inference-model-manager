import boto3
import pytest
import requests
from retrying import retry
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


@pytest.fixture(scope="session")
def configuration():
    return config.load_kube_config()


@pytest.fixture(scope="session")
def api_instance():
    return client.CoreV1Api(client.ApiClient(configuration()))


@pytest.fixture(scope="session")
def rbac_api_instance():
    return client.RbacAuthorizationV1Api(client.ApiClient(configuration()))


@pytest.fixture(scope="session")
def get_k8s_custom_obj_client(configuration):
    custom_obj_api_instance = client.CustomObjectsApi(client.ApiClient(configuration))
    return custom_obj_api_instance


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
def endpoint(function_context, get_k8s_custom_obj_client):
    namespace = TENANT_NAME
    metadata = {"name": "predict"}
    spec = {
        'modelName': 'resnet',
        'modelVersion': 1,
        'endpointName': 'predict',
        'subjectName': 'client',
        'replicas': 1,
        'resources': ENDPOINT_RESOURCES
    }
    body = {"spec": spec, 'kind': CRD_KIND, "replicas": 1,
            "apiVersion": CRD_API_VERSION,  "metadata": metadata}
    get_k8s_custom_obj_client. \
        create_namespaced_custom_object(CRD_GROUP, CRD_VERSION, namespace, CRD_PLURAL, body)
    object_to_delete = {'name': "predict", 'namespace': namespace}
    function_context.add_object(object_type='CRD', object_to_delete=object_to_delete)
    return namespace, body


@retry(stop_max_attempt_number=3, wait_fixed=200)
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
    api_response = api_instance.create_namespaced_resource_quota(namespace=namespace, body=body)
    return quota


@pytest.fixture(scope="function")
def tenant(api_instance, minio_client, function_context):
    name = TENANT_NAME
    name_object = client.V1ObjectMeta(name=name)
    namespace = client.V1Namespace(metadata=name_object)
    api_instance.create_namespace(namespace)
    quota = resource_quota(api_instance, quota=TENANT_RESOURCES)
    minio_client.create_bucket(Bucket=name)
    function_context.add_object(object_type='tenant', object_to_delete={'name': name})
    return name, quota


@pytest.fixture(scope="session")
def fake_tenant():
    name = TENANT_NAME + '-fake'
    quota = {}
    return name, quota
