import falcon
from falcon.media.validators import jsonschema

from management_api.config import RequiredParameters
from management_api.utils.logger import get_logger
from management_api.utils.parse_request import get_body, get_params
from management_api.authenticate import get_namespace

from management_api.endpoints.endpoint_utils import create_endpoint, delete_endpoint, \
    scale_endpoint, update_endpoint, view_endpoint, list_endpoints

from management_api.schemas.loadschema import endpoint_post_schema, endpoint_delete_schema


logger = get_logger(__name__)


class Endpoints(object):
    def on_get(self, req, resp):
        namespace = get_namespace(req)
        endpoints = list_endpoints(namespace)
        resp.status = falcon.HTTP_200
        resp.body = endpoints

    @jsonschema.validate(endpoint_post_schema)
    def on_post(self, req, resp):
        namespace = get_namespace(req)
        body = get_body(req)
        endpoint_url = create_endpoint(parameters=body, namespace=namespace)
        resp.status = falcon.HTTP_200
        resp.body = 'Endpoint created\n {}'.format(endpoint_url)

    @jsonschema.validate(endpoint_delete_schema)
    def on_delete(self, req, resp):
        namespace = get_namespace(req)
        body = get_body(req)
        endpoint_url = delete_endpoint(parameters=body, namespace=namespace)
        resp.status = falcon.HTTP_200
        resp.body = 'Endpoint {} deleted\n'.format(endpoint_url)


class EndpointPatch(object):

    def patch(self, parameters, namespace):
        pass

    def on_patch(self, req, resp, endpoint_name):
        namespace = get_namespace(req)
        body = get_body(req)
        get_params(body, required_keys=self.required_parameters)
        body['endpointName'] = endpoint_name
        endpoint_url = self.patch(parameters=body, namespace=namespace)
        body.pop('endpointName')
        message = 'Endpoint {} patched successfully. New values: {}\n'.format(endpoint_url, body)
        resp.status = falcon.HTTP_200  # This is the default status
        resp.body = message
        logger.info(message)


class EndpointScale(EndpointPatch):
    required_parameters = RequiredParameters.SCALE_ENDPOINT

    def patch(self, parameters, namespace):
        return scale_endpoint(parameters, namespace)


class EndpointUpdate(EndpointPatch):
    required_parameters = RequiredParameters.UPDATE_ENDPOINT

    def patch(self, parameters, namespace):
        return update_endpoint(parameters, namespace)


class EndpointView(object):
    def on_get(self, req, resp, endpoint_name):
        namespace = get_namespace(req)
        endpoint = view_endpoint(endpoint_name=endpoint_name, namespace=namespace)
        resp.status = falcon.HTTP_200
        resp.body = endpoint
