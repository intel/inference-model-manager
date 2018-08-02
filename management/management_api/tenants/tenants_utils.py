import falcon
import json
import base64

from botocore.exceptions import ClientError
from cryptography import x509
from cryptography.hazmat.backends import default_backend
from kubernetes import client
from kubernetes.client.rest import ApiException

from management_api.config import api_instance, minio, CERT_SECRET_NAME
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
    except KeyError as keyError:
        logger.error('{} parameter required'.format(keyError))
        raise falcon.HTTPBadRequest('{} parameter required'.format(keyError))
    logger.info('Creating new tenant: name={}, cert={}, scope={}'
                .format(name, cert, scope))
    return name, cert, scope


def create_namespace(name):
    name_object = client.V1ObjectMeta(name=name)
    namespace = client.V1Namespace(metadata=name_object)
    try:
        api_instance.create_namespace(namespace)
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


def create_bucket(name):
    try:
        response = minio.create_bucket(Bucket=name)
    except ClientError as clientError:
        logger.error('ClientError occurred: {}'.format(clientError))
        raise falcon.HTTPBadRequest('ClientError occurred: {}'
                                    .format(clientError))
    except Exception as e:
        logger.error('An error occurred during bucket creation: {}'.format(e))
        raise falcon.HTTPBadRequest('An error occurred during bucket '
                                    'creation: {}'.format(e))
    logger.info('Bucket created: {}'.format(response))


def initial_cert_validation(cert):
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


def create_secret(name, cert):
    cert_secret_metadata = client.V1ObjectMeta(name=CERT_SECRET_NAME)
    cert_secret_data = {"ca.crt": cert}
    cert_secret = client.V1Secret(api_version="v1", data=cert_secret_data,
                                  kind="Secret", metadata=cert_secret_metadata,
                                  type="Opaque")
    try:
        api_instance.create_namespaced_secret(namespace=name, body=cert_secret)
    except ApiException as apiException:
        logger.error('Did not create secret: {}'.format(apiException))
        raise falcon.HTTPBadRequest('Did not create secret: {}'
                                    .format(apiException))
    logger.info('Secret {} created'.format(CERT_SECRET_NAME))
