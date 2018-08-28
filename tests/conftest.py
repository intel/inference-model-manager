import boto3
from botocore.client import Config
import pytest
from retrying import retry
from kubernetes import config, client
from kubernetes.client.rest import ApiException

from management_api_tests.config import MINIO_SECRET_ACCESS_KEY, MINIO_ACCESS_KEY_ID, \
    MINIO_REGION, MINIO_ENDPOINT_ADDR, SIGNATURE_VERSION, CRD_GROUP, CRD_VERSION, CRD_PLURAL, \
    CRD_API_VERSION, CRD_KIND
from management_api_tests.context import Context


@pytest.fixture(scope="session")
def configuration():
    return config.load_kube_config()


@pytest.fixture(scope="session")
def api_instance():
    return client.CoreV1Api(client.ApiClient(configuration()))


@pytest.fixture(scope="session")
def get_k8s_custom_obj_client(configuration):
    custom_obj_api_instance = client.CustomObjectsApi(client.ApiClient(configuration))
    return custom_obj_api_instance


@pytest.fixture(scope="function")
def function_context(request, get_k8s_custom_obj_client, api_instance, minio_resource):
    context = Context(k8s_client=api_instance, k8s_client_custom=get_k8s_custom_obj_client,
                      minio_resource_client=minio_resource)
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
def create_endpoint(function_context, get_k8s_custom_obj_client):
    namespace = 'default'
    metadata = {"name": "predict"}
    spec = {
        'modelName': 'resnet',
        'modelVersion': 1,
        'endpointName': 'predict',
        'subjectName': 'client',
        'replicas': 1
    }
    body = {"spec": spec, 'kind': CRD_KIND, "replicas": 1,
            "apiVersion": CRD_API_VERSION,  "metadata": metadata}
    api_response = get_k8s_custom_obj_client. \
        create_namespaced_custom_object(CRD_GROUP, CRD_VERSION, namespace, CRD_PLURAL, body)
    object_to_delete = {'name': "predict", 'namespace': namespace}
    function_context.add_object(object_type='CRD', object_to_delete=object_to_delete)
    return api_response, namespace, body


@retry(stop_max_attempt_number=3, wait_fixed=200)
def get_all_pods_in_namespace(k8s_client, namespace, label_selector=''):
    try:
        api_response = k8s_client.list_namespaced_pod(namespace=namespace,
                                                      label_selector=label_selector)
    except ApiException as e:
        print("Exception when calling CoreV1Api->list_pod_for_all_namespaces: %s\n" % e)

    return api_response
