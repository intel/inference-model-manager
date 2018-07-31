import falcon
import json
import base64

from kubernetes import client
from kubernetes.client.rest import ApiException
from botocore.exceptions import ClientError, BotoCoreError

from management_api.logger import get_logger
from management_api.config import api_instance, minio, CERT_SECRET_NAME

from cryptography import x509
from cryptography.hazmat.backends import default_backend

logger = get_logger(__name__)


class Tenants(object):

    def initial_cert_validation(self, cert):
        pem_data = base64.b64decode(cert)
        x509.load_pem_x509_certificate(pem_data, default_backend())
    
    def on_post(self, req, resp):
        """Handles POST requests"""
        try:
            body = json.loads(req.stream.read().decode("utf-8"))
        except:
            logger.error('Request body is not a proper json')
            raise falcon.HTTPBadRequest('Request body is not a proper json')

        name = None
        cert = None
        scope = None
        try:
            name = body['name']
            cert = body['cert']
            scope = body['scope']
            logger.info('Creating new tenant: name={}, cert={}, scope={}'.format(name, cert, scope))
        except KeyError as keyError:
            logger.error('{} parameter required'.format(keyError))
            raise falcon.HTTPBadRequest('{} parameter required'.format(keyError))
        
        try:
            self.initial_cert_validation(cert)
        except TypeError:
            logger.error('Incorrect certificate data in request body. Base64 decoding failure.')
            raise falcon.HTTPError(status=falcon.HTTP_400, description='Incorrect certificate data in request body. Base64 decoding failure.')
        except ValueError:
            logger.error('Incorrect certificate format')
            raise falcon.HTTPError(status=falcon.HTTP_400, description='Incorrect certificate format')


        logger.info('Initial certificate validation succeeded')

        name_object = client.V1ObjectMeta(name=name)
        namespace = client.V1Namespace(metadata=name_object)
        
        try:
            api_response = api_instance.create_namespace(namespace)
        except ApiException as apiException:
            logger.error('Did not create namespace: {}'.format(apiException))
            raise falcon.HTTPError(status=falcon.HTTP_400, description='Did not create namespace: {}'.format(apiException))

        logger.info("Namespace {} created".format(name))			

        try:
            response = minio.create_bucket(Bucket=name)
        except ClientError as clientError:
            logger.error('ClientError occurred: {}'.format(clientError))
            raise falcon.HTTPError(status=falcon.HTTP_400, description='ClientError occurred: {}'.format(clientError))
        except Exception as e:
            logger.error('An error occurred: {}'.format(e))
            raise falcon.HTTPError(status=falcon.HTTP_400, description='An error occurred: {}'.format(e))

        logger.info('Bucket {} created'.format(name))

        cert_secret_metadata = client.V1ObjectMeta(name=CERT_SECRET_NAME)
        cert_secret_data = {"ca.crt" : cert}
        cert_secret = client.V1Secret(api_version="v1", data=cert_secret_data, kind="Secret", metadata=cert_secret_metadata, type="Opaque")
		
        try:
            api_response = api_instance.create_namespaced_secret(namespace=name, body=cert_secret)
        except ApiException as apiException:
            logger.error('Did not create secret: {}'.format(apiException))
            raise falcon.HTTPError(status=falcon.HTTP_400, description='Did not create secret: {}'.format(apiException))		
        

        logger.info('Secret {} created'.format(CERT_SECRET_NAME))
        logger.info('Tenant creation completed successfully')
        resp.status = falcon.HTTP_200
        resp.body = 'Tentant {} created\n'.format(name)

    def on_delete(self, req, resp):
        """Handles DELETE requests"""
        resp.status = falcon.HTTP_200  # This is the default status
        resp.body = 'Delete completed'
