import falcon
import json

from kubernetes import client
from kubernetes.client.rest import ApiException
from botocore.exceptions import ClientError, BotoCoreError

from management_api.logger import get_logger
from management_api.config import api_instance, minio

logger = get_logger(__name__)


class Tenants(object):
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
        
        name_object = client.V1ObjectMeta(name=name)
        namespace = client.V1Namespace(metadata=name_object)
        
        try:
            api_response = api_instance.create_namespace(namespace)
            logger.info("Namespace {} created".format(name))			
        except ApiException as apiException:
            logger.error('Did not create namespace: {}'.format(apiException))
            raise falcon.HTTPError(status=falcon.HTTP_400, description='Did not create namespace: {}'.format(apiException))

        logger.info('Namespace created: {}'.format(api_response))

        try:
            response = minio.create_bucket(Bucket=name)
        except ClientError as clientError:
            logger.error('ClientError occurred: {}'.format(clientError))
            raise falcon.HTTPError(status=falcon.HTTP_400, description='ClientError occurred: {}'.format(clientError))
        except Exception as e:
            logger.error('An error occurred: {}'.format(e))
            raise falcon.HTTPError(status=falcon.HTTP_400, description='An error occurred: {}'.format(e))

        logger.info('Bucket created: {}'.format(response))

        resp.status = falcon.HTTP_200
        resp.body = 'Namespace and bucket {} created\n'.format(name)

    def on_delete(self, req, resp):
        """Handles DELETE requests"""
        resp.status = falcon.HTTP_200  # This is the default status
        resp.body = 'Delete completed'

