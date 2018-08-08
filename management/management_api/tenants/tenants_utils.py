import falcon
import json
import base64
import re

from botocore.exceptions import ClientError
from cryptography import x509
from cryptography.hazmat.backends import default_backend
from kubernetes import client
from kubernetes.client.rest import ApiException
from retrying import retry

from management_api.config import CERT_SECRET_NAME, api_instance, \
    minio_resource, minio_client
from management_api.utils.logger import get_logger


logger = get_logger(__name__)


def get_body(req):
    try:
        body = json.loads(req.stream.read().decode("utf-8"))
    except IOError as ie:
        logger.error('Request body is not a proper json: {}'.format(ie))
        raise falcon.HTTPBadRequest('Request body is not a proper json: {}'
                                    .format(ie))
    except Exception as e:
        logger.error('Error occurred during decoding request body: {}'
                     .format(e))
        raise falcon.HTTPBadRequest('Error occurred during decoding request '
                                    'body: {}'.format(e))
    return body


def get_params(body):
    try:
        name = body['name']
        cert = body['cert']
        scope = body['scope']
        quota = body['quota']
    except KeyError as keyError:
        logger.error('{} parameter required'.format(keyError))
        raise falcon.HTTPBadRequest('{} parameter required'.format(keyError))
    return name, cert, scope, quota


def create_tenant(name, cert, scope, quota):
    logger.info('Creating new tenant: name={}, cert={}, scope={}, quota={}'
                .format(name, cert, scope, quota)) 
    if is_cert_valid(cert):
            validate_quota(quota)
            create_namespace(name, quota)
            create_bucket(minio_client, name)
            create_secret(name, cert)
            create_resource_quota(name, quota)
    return True


def create_namespace(name, quota):
    if 'maxEndpoints' in quota:
        name_object = client.V1ObjectMeta(name=name,
                                          annotations={'maxEndpoints': quota.pop('maxEndpoints')})
    else:
        name_object = client.V1ObjectMeta(name=name)
    namespace = client.V1Namespace(metadata=name_object)
    try:
        response = api_instance.create_namespace(namespace)
    except ApiException as apiException:
        logger.error('Did not create namespace: {}'.format(apiException))
        raise falcon.HTTPBadRequest('Did not create namespace: {}'
                                    .format(apiException))
    except Exception as e:
        logger.error('An error occurred during namespace creation: {}'
                     .format(e))
        raise falcon.HTTPBadRequest('An error occurred during namespace '
                                    'creation: {}'.format(e))
    logger.info("Namespace {} created".format(name))
    return response


def create_bucket(minio_client, name):
    error_occurred = False
    try:
        response = minio_client.create_bucket(Bucket=name)
    except ClientError as clientError:
        error_occurred = True
        logger.error('ClientError occurred: {}'.format(clientError))
        raise falcon.HTTPBadRequest('ClientError occurred: {}'
                                    .format(clientError))
    except Exception as e:
        error_occurred = True
        logger.error('An error occurred during bucket creation: {}'.format(e))
        raise falcon.HTTPBadRequest('An error occurred during bucket '
                                    'creation: {}'.format(e))
    finally:
        if error_occurred:
            delete_namespace(name)
    logger.info('Bucket created: {}'.format(response))
    return response


def is_cert_valid(cert):
    try:
        pem_data = base64.b64decode(cert)
        x509.load_pem_x509_certificate(pem_data, default_backend())
    except TypeError:
        logger.error('Incorrect certificate data in request body. '
                     'Base64 decoding failure.')
        raise falcon.HTTPBadRequest('Incorrect certificate data in request body'
                                    '. Base64 decoding failure.')
    except ValueError:
        logger.error('Incorrect certificate format')
        raise falcon.HTTPBadRequest('Incorrect certificate format')
    logger.info('Initial certificate validation succeeded')
    return True


def create_secret(name, cert):
    cert_secret_metadata = client.V1ObjectMeta(name=CERT_SECRET_NAME)
    cert_secret_data = {"ca.crt": cert}
    cert_secret = client.V1Secret(api_version="v1", data=cert_secret_data,
                                  kind="Secret", metadata=cert_secret_metadata,
                                  type="Opaque")
    try:
        response = api_instance.create_namespaced_secret(namespace=name,
                                                         body=cert_secret)
    except ApiException as apiException:
        delete_bucket(minio_resource, name)
        delete_namespace(name)
        logger.error('Did not create secret: {}'.format(apiException))
        raise falcon.HTTPBadRequest('Did not create secret: {}'
                                    .format(apiException))
    logger.info('Secret {} created'.format(CERT_SECRET_NAME))
    return response


def validate_quota(quota):
    int_keys = ['maxEndpoints', 'requests.cpu', 'limits.cpu']
    alpha_keys = ['requests.memory', 'limits.memory']
    regex_k8s = '^([+]?[0-9.]+)([eEinumkKMGTP]*[+]?[0-9]*)$'

    test_quota = dict(quota)
    for key, value in quota.items():
        if key in int_keys:
            if not value.isdigit() > 0:
                logger.error('Invalid value {} of {} field: '
                             'must be integer greater than or equal to 0'.format(value, key))
                raise falcon.HTTPBadRequest('Invalid value {} of {} field: '
                             'must be integer greater than or equal to 0'.format(value, key))
            test_quota.pop(key)
        if key in alpha_keys:
            if not re.match(regex_k8s, value):
                logger.error('Invalid value {} of {} field. '
                             'Please provide value that matches Kubernetes convention. '
                             'Some example values: '
                             '\'1Gi\', \'200Mi\', \'300m\''.format(value, key))
                raise falcon.HTTPBadRequest('Invalid value {} of {} field. '
                             'Please provide value that matches Kubernetes convention. '
                             'Some example values: '
                             '\'1Gi\', \'200Mi\', \'300m\''.format(value, key))
            test_quota.pop(key)

    if test_quota:
        logger.info("There's some redundant values provided that won't be used:")
        for key, value in test_quota.items():
            logger.info(key + ": " + value)
            quota.pop(key)
    logger.info('Resource quota {} is valid'.format(quota))
    return True


def create_resource_quota(name, quota):
    name_object = client.V1ObjectMeta(name=name)
    resource_quota_spec = client.V1ResourceQuotaSpec(hard=quota)
    body = client.V1ResourceQuota(spec=resource_quota_spec, metadata=name_object)

    try:
        response = api_instance.create_namespaced_resource_quota(name, body)
        logger.info("Resource quota {} created".format(quota))
    except ApiException as apiException:
        delete_bucket(minio_resource, name)
        delete_namespace(name)
        logger.error("Resource quota not created: {}".format(apiException))
        raise falcon.HTTPError(status=falcon.HTTP_400,
                               description='An error occured during resource quota creation: {}'
                               .format(apiException))
    return response


@retry(stop_max_attempt_number=5, wait_fixed=2000)
def delete_bucket(name):
    try:
        bucket = minio_resource.Bucket(name)
        bucket.objects.all().delete()
        response = bucket.delete()
    except ClientError as clientError:
        error_code = int(clientError.response['Error']['Code'])
        logger.error('Error occurred during bucket deletion: {}'.
                     format(clientError))
        if error_code != 404:
            raise falcon.HTTPBadRequest('Error occurred during bucket '
                                        'deletion: {}'.format(clientError))
    logger.info('Bucket {} deleted'.format(name))
    return response


@retry(stop_max_attempt_number=5, wait_fixed=2000)
def delete_namespace(name):
    body = client.V1DeleteOptions()
    try:
        response = api_instance.delete_namespace(name, body,
                                                 propagation_policy='Background')
    except ApiException as apiException:
        logger.error('Error occurred during namespace deletion: {}'.
                     format(apiException))
        raise falcon.HTTPBadRequest('Error occurred during namespace '
                                    'deletion: {}'.format(apiException))
    logger.info('Namespace {} deleted'.format(name))
    return response

