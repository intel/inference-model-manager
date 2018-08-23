import logging

import boto3
import pytest
from botocore.client import Config
from botocore.exceptions import ClientError
from kubernetes import config, client
from kubernetes.client.rest import ApiException
from time import sleep

from management_api_tests.config import MINIO_SECRET_ACCESS_KEY, MINIO_ACCESS_KEY_ID, MINIO_REGION, \
    MINIO_ENDPOINT_ADDR, SIGNATURE_VERSION, CRD_VERSION, CRD_PLURAL, CRD_KIND, CRD_GROUP, \
    CRD_API_VERSION


@pytest.fixture(scope="session")
def configuration():
    return config.load_kube_config()


@pytest.fixture(scope="session")
def api_instance():
    return client.CoreV1Api(client.ApiClient(configuration()))


@pytest.fixture(scope="session")
def custom_obj_api_instance():
    return client.CustomObjectsApi(client.ApiClient(configuration()))


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


def delete_namespace_bucket(name):
    try:
        bucket = minio_resource().Bucket(name)
        bucket.objects.all().delete()
        bucket.delete()
    except ClientError as clientError:
        logging.error(clientError)
    body = client.V1DeleteOptions()
    try:
        api_instance().delete_namespace(name, body)
    except ApiException as apiException:
        logging.error(apiException)
    sleep(2)
    logging.info('{} deleted.'.format(name))


def create_default_endpoint():
    spec = {
        'modelName': 'resnet',
        'modelVersion': 1,
        'endpointName': 'predict',
        'subjectName': 'client',
        'replicas': 1
    }
    metadata = {"name": "predict"}
    body = {"apiVersion": CRD_API_VERSION, "kind": CRD_KIND, "spec": spec, "metadata": metadata}

    try:
        custom_obj_api_instance(). \
            create_namespaced_custom_object(CRD_GROUP, CRD_VERSION, 'default', CRD_PLURAL, body)
    except ApiException as e:
        logging.error('An error occurred during endpoint creation: {}'.format(e))
    logging.info('Default endpoint created')


def delete_default_endpoint():
    delete_body = client.V1DeleteOptions()
    try:
        custom_obj_api_instance(). \
            delete_namespaced_custom_object(CRD_GROUP, CRD_VERSION, 'default', CRD_PLURAL,
                                            'predict', delete_body,
                                            grace_period_seconds=0)
    except ApiException as e:
        logging.error('Error occurred during endpoint deletion: {}'.format(e))
    logging.info('Default endpoint deleted')